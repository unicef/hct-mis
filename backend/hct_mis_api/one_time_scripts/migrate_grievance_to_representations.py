import copy
from itertools import chain
from typing import Any, Optional, Union

from django.db.models import Count, Q, QuerySet
from django.utils import timezone

from hct_mis_api.apps.accountability.models import Feedback, FeedbackMessage, Message
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string, encode_id_base64
from hct_mis_api.apps.grievance.models import (
    GrievanceDocument,
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketNote,
    TicketPaymentVerificationDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.household.models import (
    BankAccountInfo,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import Payment, PaymentRecord
from hct_mis_api.apps.program.models import Program
from hct_mis_api.one_time_scripts.migrate_data_to_representations import (
    get_household_representation_per_program_by_old_household_id,
    get_individual_representation_per_program_by_old_individual_id,
)

BATCH_SIZE = 500


def migrate_grievance_to_representations() -> None:
    """
    Migrate grievance tickets and feedback into representations.
    """
    model_list = [
        TicketComplaintDetails,
        TicketSensitiveDetails,
        TicketPaymentVerificationDetails,
        TicketIndividualDataUpdateDetails,
        TicketHouseholdDataUpdateDetails,
        TicketAddIndividualDetails,
        TicketDeleteIndividualDetails,
        TicketDeleteHouseholdDetails,
        TicketSystemFlaggingDetails,
        TicketPositiveFeedbackDetails,
        TicketNegativeFeedbackDetails,
        TicketReferralDetails,
        TicketNeedsAdjudicationDetails,
        GrievanceTicket,
        TicketNote,
        GrievanceDocument,
        Message,
        Feedback,
        FeedbackMessage,
    ]
    for model in model_list:
        model._meta.get_field("created_at").auto_now_add = False
    try:
        migrate_grievance_tickets()
        migrate_messages()
        migrate_feedback()
    finally:
        for model in model_list:
            model._meta.get_field("created_at").auto_now_add = True


def migrate_grievance_tickets() -> None:
    """
    Migrate grievance tickets into representations.
    """
    print("Handle payment related tickets")
    handle_payment_related_tickets()
    print("Handle non payment related tickets")
    handle_non_payment_related_tickets()
    print("Handle tickets not connected to any program")
    handle_non_program_tickets()


def handle_payment_related_tickets() -> None:
    """
    Assign grievance tickets to representations. Applied for tickets connected to specific payment.
    Handle TicketComplaintDetails, TicketSensitiveDetails, TicketPaymentVerificationDetails with related payment_obj
    """

    # Fetch all objects of TicketComplaintDetails and TicketSensitiveDetails with non-null payment_obj
    complaint_tickets_with_payments = TicketComplaintDetails.objects.select_related(
        "household",
        "individual",
    ).filter(payment_object_id__isnull=False)
    sensitive_tickets_with_payments = TicketSensitiveDetails.objects.select_related(
        "household",
        "individual",
    ).filter(payment_object_id__isnull=False)

    complaint_and_sensitive_details_tickets = chain(complaint_tickets_with_payments, sensitive_tickets_with_payments)

    # Update household and individual fields based on payment_obj for TicketComplaintDetails and TicketSensitiveDetails
    for ticket in complaint_and_sensitive_details_tickets:
        household, individual, program = get_program_and_representations_for_payment(ticket)
        ticket.household = household
        ticket.individual = individual
        if program:
            ticket.ticket.programs.set([program])

    # Perform a bulk update for the household and individual fields of TicketComplaintDetails and TicketSensitiveDetails
    TicketComplaintDetails.objects.bulk_update(complaint_tickets_with_payments, ["household", "individual"])
    TicketSensitiveDetails.objects.bulk_update(sensitive_tickets_with_payments, ["household", "individual"])

    # Update household_unicef_id for all related GrievanceTickets
    # Fetch the GrievanceTickets related to the updated objects
    grievance_tickets = GrievanceTicket.objects.filter(
        Q(complaint_ticket_details__in=complaint_tickets_with_payments)
        | Q(sensitive_ticket_details__in=sensitive_tickets_with_payments)
    ).distinct()
    # Update household_unicef_id for each GrievanceTicket using bulk_update
    for grievance_ticket in grievance_tickets:
        related_ticket = getattr(grievance_ticket, "complaint_ticket_details", None) or getattr(
            grievance_ticket, "sensitive_ticket_details", None
        )
        household_unicef_id = getattr(related_ticket.household, "unicef_id", None)
        grievance_ticket.household_unicef_id = household_unicef_id

    GrievanceTicket.objects.bulk_update(grievance_tickets, ["household_unicef_id"])

    # Update programs for TicketPaymentVerificationDetails with payment_obj
    payment_verification_tickets = (
        TicketPaymentVerificationDetails.objects.select_related(
            "payment_verification",
        )
        .filter(
            payment_verification__isnull=False,
            payment_verification__payment_object_id__isnull=False,
            ticket__programs=None,
        )
        .distinct()
        .iterator()
    )
    for payment_verification_ticket in payment_verification_tickets:
        payment_obj = payment_verification_ticket.payment_verification.payment_obj
        if isinstance(payment_obj, Payment):
            program = payment_obj.parent.target_population.program
        elif isinstance(payment_obj, PaymentRecord):
            program = payment_obj.target_population.program
        else:
            program = None
        if program:
            payment_verification_ticket.ticket.programs.set([program])


def get_program_and_representations_for_payment(ticket: Union[TicketComplaintDetails, TicketSensitiveDetails]) -> tuple:
    if isinstance(ticket.payment_obj, Payment):
        program = ticket.payment_obj.parent.target_population.program
    elif isinstance(ticket.payment_obj, PaymentRecord):
        program = ticket.payment_obj.target_population.program
    else:
        program = None
    household_representation = (
        get_household_representation_per_program_by_old_household_id(
            program=program, old_household_id=ticket.household.copied_from_id
        )
        if ticket.household
        else None
    )
    individual_representation = (
        get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=ticket.individual.copied_from_id,
        )
        if ticket.individual
        else None
    )
    return household_representation, individual_representation, program


def handle_non_payment_related_tickets() -> None:
    """
    Copy grievance tickets to representations.
    Applied for tickets not connected to specific payment but connected to household or its individual.
    """
    print("Handle TicketComplaintDetails without payment")
    handle_complaint_tickets_without_payments()
    print("Handle TicketSensitiveDetails without payment")
    handle_sensitive_tickets_without_payments()
    print("Handle TicketHouseholdDataUpdateDetails")
    handle_household_data_update_tickets()
    print("Handle TicketIndividualDataUpdateDetails")
    handle_individual_data_update_tickets()
    print("Handle TicketAddIndividualDetails")
    handle_add_individual_tickets()
    print("Handle TicketDeleteIndividualDetails")
    handle_delete_individual_tickets()
    print("Handle TicketDeleteHouseholdDetails")
    handle_delete_household_tickets()
    print("Handle TicketSystemFlaggingDetails")
    handle_system_flagging_details_tickets()
    print("Handle TicketPositiveFeedbackDetails")
    handle_positive_feedback_tickets()
    print("Handle TicketNegativeFeedbackDetails")
    handle_negative_feedback_tickets()
    print("Handle TicketReferralDetails")
    handle_referral_tickets()
    print("Handle TicketNeedsAdjudicationDetails")
    handle_needs_adjudication_tickets()


def handle_complaint_tickets_without_payments() -> None:
    complaint_tickets_without_payments = TicketComplaintDetails.objects.select_related(
        "ticket",
        "household",
        "individual",
    ).filter(payment_object_id__isnull=True, ticket__programs=None)
    handle_closed_tickets_with_household_and_individual(complaint_tickets_without_payments)
    handle_active_tickets_with_household_and_individual(complaint_tickets_without_payments)


def handle_sensitive_tickets_without_payments() -> None:
    sensitive_tickets_without_payments = TicketSensitiveDetails.objects.select_related(
        "ticket",
        "household",
        "individual",
    ).filter(payment_object_id__isnull=True, ticket__programs=None)
    handle_closed_tickets_with_household_and_individual(sensitive_tickets_without_payments)
    handle_active_tickets_with_household_and_individual(sensitive_tickets_without_payments)


def handle_closed_tickets_with_household_and_individual(tickets: QuerySet) -> None:
    """
    In case of closed complaint ticket, we need to make sure it is not assigned to household representation
    from different program than individual representation.
    """
    print("Handle closed tickets with household and individual")
    closed_tickets = tickets.filter(ticket__status=GrievanceTicket.STATUS_CLOSED)
    for closed_ticket in closed_tickets.iterator():
        if closed_ticket.household:
            program = closed_ticket.household.program
        elif closed_ticket.individual:
            program = closed_ticket.individual.program
        else:
            program = None

        if closed_ticket.household and closed_ticket.individual:
            individual_representation = get_individual_representation_per_program_by_old_individual_id(
                program=program,
                old_individual_id=closed_ticket.individual.copied_from_id,
            )
            closed_ticket.individual = individual_representation
            closed_ticket.save(update_fields=["individual"])

        if program:
            closed_ticket.ticket.programs.set([program])


def handle_active_tickets_with_household_and_individual(tickets: QuerySet) -> None:
    """
    For active complaint tickets, we need to copy tickets for every household/individual representation
    """
    print("Handle active tickets with household and individual")
    active_tickets = tickets.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED).iterator()

    for active_ticket in active_tickets:
        current_program = None
        if active_ticket.individual:
            individual_representations = active_ticket.individual.copied_to.all()
            current_program = active_ticket.individual.program
        else:
            individual_representations = Individual.objects.none()
        if active_ticket.household:
            household_representations = active_ticket.household.copied_to.all()
            current_program = active_ticket.household.program
        else:
            household_representations = Household.objects.none()

        if current_program:
            individual_programs = (
                individual_representations.exclude(program=current_program).values_list("program", flat=True).distinct()
            )
            household_programs = (
                household_representations.exclude(program=current_program).values_list("program", flat=True).distinct()
            )

            all_programs = household_programs.union(individual_programs)

            for program in all_programs:
                copy_ticket_with_household_and_individual(active_ticket, program)

            handle_current_program_ticket_with_household_and_individual(active_ticket, current_program)


def copy_ticket_with_household_and_individual(active_ticket: Any, program: Program) -> None:
    ticket_copy = copy.deepcopy(active_ticket)
    ticket_copy.pk = None
    if ticket_copy.household:
        household_representation = get_household_representation_per_program_by_old_household_id(
            program=program,
            old_household_id=ticket_copy.household.copied_from_id,
        )
        ticket_copy.household = household_representation

    if ticket_copy.individual:
        individual_representation = get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=ticket_copy.individual.copied_from_id,
        )
        ticket_copy.individual = individual_representation

    ticket_copy = copy_grievance_ticket(ticket_copy, program, active_ticket)
    ticket_copy.save()


def handle_current_program_ticket_with_household_and_individual(
    current_program_ticket: Any, current_program: Program
) -> None:
    current_program_ticket.ticket.programs.set([current_program])

    if current_program_ticket.household and current_program_ticket.individual:
        individual_representation = get_individual_representation_per_program_by_old_individual_id(
            program=current_program,
            old_individual_id=current_program_ticket.individual.copied_from_id,
        )
        current_program_ticket.individual = individual_representation

        current_program_ticket.save(update_fields=["individual"])


def handle_tickets_with_household(model: Any) -> None:
    tickets_with_hh = (
        model.objects.select_related(
            "ticket",
            "household",
            "household__program",
        )
        .prefetch_related(
            "household__copied_to",
        )
        .filter(household__isnull=False, ticket__programs=None)
    )
    # Handle closed tickets
    for closed_ticket in tickets_with_hh.filter(ticket__status=GrievanceTicket.STATUS_CLOSED).iterator():
        closed_ticket.ticket.programs.set([closed_ticket.household.program])

    # Handle active tickets
    for active_ticket in tickets_with_hh.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED).iterator():
        if active_ticket.household:
            household_representations = active_ticket.household.copied_to.all()

            # Handle current program ticket
            current_program = active_ticket.household.program
            active_ticket.ticket.programs.set([current_program])

            household_programs = (
                household_representations.values_list("program", flat=True).distinct().exclude(program=current_program)
            )

            for program in household_programs.iterator():
                copy_ticket_with_household(active_ticket, program)

            if hasattr(active_ticket, "role_reassign_data"):
                handle_role_reassign_data(active_ticket, current_program)


def copy_ticket_with_household(active_ticket: Any, program: Program) -> None:
    ticket = copy.deepcopy(active_ticket)
    if hasattr(ticket, "role_reassign_data"):
        ticket = handle_role_reassign_data(ticket, program)
    household_representation = get_household_representation_per_program_by_old_household_id(
        program=program,
        old_household_id=ticket.household.copied_from_id,
    )
    ticket.household = household_representation

    ticket.pk = None
    ticket = copy_grievance_ticket(ticket, program, active_ticket)
    ticket.save()


def handle_tickets_with_individual(model: Any, individual_field_name: str = "individual") -> None:
    tickets_with_ind = (
        model.objects.select_related(
            "ticket",
            individual_field_name,
            f"{individual_field_name}__program",
        )
        .prefetch_related(
            f"{individual_field_name}__copied_to",
        )
        .filter(ticket__programs=None, **{f"{individual_field_name}__isnull": False})
    )
    # Handle closed tickets
    for closed_ticket in tickets_with_ind.filter(ticket__status=GrievanceTicket.STATUS_CLOSED).iterator():
        closed_ticket.ticket.programs.set([getattr(closed_ticket, individual_field_name).program])

    # Handle active tickets
    for active_ticket in tickets_with_ind.exclude(ticket__status=GrievanceTicket.STATUS_CLOSED).iterator():
        if getattr(active_ticket, individual_field_name):
            individual_representations = getattr(active_ticket, individual_field_name).copied_to.all()

            # Handle current program ticket
            current_program = getattr(active_ticket, individual_field_name).program
            active_ticket.ticket.programs.set([current_program])

            individual_programs = (
                individual_representations.values_list("program", flat=True).distinct().exclude(program=current_program)
            )

            for program in individual_programs.iterator():
                copy_ticket_with_individual(active_ticket, program, individual_field_name=individual_field_name)

            if hasattr(active_ticket, "role_reassign_data"):
                handle_role_reassign_data(active_ticket, current_program)
            if hasattr(active_ticket, "individual_data") and isinstance(
                active_ticket, TicketIndividualDataUpdateDetails
            ):
                handle_individual_data(active_ticket, current_program)


def copy_ticket_with_individual(active_ticket: Any, program: Program, individual_field_name: str) -> None:
    ticket = copy.deepcopy(active_ticket)
    if hasattr(ticket, "role_reassign_data"):
        ticket = handle_role_reassign_data(ticket, program)
    if hasattr(active_ticket, "individual_data") and isinstance(active_ticket, TicketIndividualDataUpdateDetails):
        handle_individual_data(ticket, program)
    individual_representation = get_individual_representation_per_program_by_old_individual_id(
        program=program,
        old_individual_id=getattr(ticket, individual_field_name).copied_from_id,
    )
    setattr(ticket, individual_field_name, individual_representation)

    ticket.pk = None
    ticket = copy_grievance_ticket(ticket, program, active_ticket)
    ticket.save()


def handle_individual_data_update_tickets() -> None:
    handle_tickets_with_individual(TicketIndividualDataUpdateDetails)


def handle_household_data_update_tickets() -> None:
    handle_tickets_with_household(TicketHouseholdDataUpdateDetails)


def handle_add_individual_tickets() -> None:
    handle_tickets_with_household(TicketAddIndividualDetails)


def handle_delete_individual_tickets() -> None:
    handle_tickets_with_individual(TicketDeleteIndividualDetails)


def handle_delete_household_tickets() -> None:
    handle_tickets_with_household(TicketDeleteHouseholdDetails)


def handle_system_flagging_details_tickets() -> None:
    handle_tickets_with_individual(TicketSystemFlaggingDetails, individual_field_name="golden_records_individual")


def handle_positive_feedback_tickets() -> None:
    positive_feedback_tickets = TicketPositiveFeedbackDetails.objects.filter(ticket__programs=None)
    handle_closed_tickets_with_household_and_individual(positive_feedback_tickets)
    handle_active_tickets_with_household_and_individual(positive_feedback_tickets)


def handle_negative_feedback_tickets() -> None:
    negative_feedback_tickets = TicketNegativeFeedbackDetails.objects.filter(ticket__programs=None)
    handle_closed_tickets_with_household_and_individual(negative_feedback_tickets)
    handle_active_tickets_with_household_and_individual(negative_feedback_tickets)


def handle_referral_tickets() -> None:
    referral_tickets = TicketReferralDetails.objects.filter(ticket__programs=None)
    handle_closed_tickets_with_household_and_individual(referral_tickets)
    handle_active_tickets_with_household_and_individual(referral_tickets)


def handle_needs_adjudication_tickets() -> None:
    needs_adjudication_tickets = (
        TicketNeedsAdjudicationDetails.objects.select_related(
            "ticket",
            "golden_records_individual",
        )
        .prefetch_related(
            "possible_duplicates",
            "selected_individuals",
        )
        .filter(ticket__programs=None)
    )

    for needs_adjudication_ticket in needs_adjudication_tickets.iterator():
        individuals = [
            needs_adjudication_ticket.golden_records_individual,
            *needs_adjudication_ticket.possible_duplicates.all(),
        ]
        program_ids = (
            Individual.objects.filter(id__in=[individual.id for individual in individuals])
            .values(
                "copied_to__program",
            )
            .annotate(program_count=Count("id"))
            .filter(program_count__gt=1)
            .values_list("copied_to__program", flat=True)
        )
        programs = Program.objects.filter(id__in=program_ids)
        if not programs:
            needs_adjudication_ticket.delete()
            continue
        current_program = programs.first()
        programs_without_current = programs.exclude(id=current_program.id)

        for program in programs_without_current:
            needs_adjudication_ticket_copy = copy.deepcopy(needs_adjudication_ticket)
            if hasattr(needs_adjudication_ticket_copy, "role_reassign_data"):
                needs_adjudication_ticket_copy = handle_role_reassign_data(needs_adjudication_ticket_copy, program)
            if hasattr(needs_adjudication_ticket_copy, "extra_data"):
                needs_adjudication_ticket_copy = handle_extra_data(needs_adjudication_ticket_copy, program)
            needs_adjudication_ticket_copy.pk = None
            # Copy Grievance Ticket
            needs_adjudication_ticket_copy = copy_grievance_ticket(
                needs_adjudication_ticket_copy,
                program,
                needs_adjudication_ticket,
            )

            possible_duplicates = [
                get_individual_representation_per_program_by_old_individual_id(
                    program=program,
                    old_individual_id=individual.copied_from_id,
                )
                for individual in individuals
            ]
            possible_duplicates = [individual for individual in possible_duplicates if individual]
            needs_adjudication_ticket_copy.golden_records_individual = possible_duplicates.pop()

            # Handle selected_individuals
            old_selected_individuals = needs_adjudication_ticket.selected_individuals.all()
            selected_individuals = [
                get_individual_representation_per_program_by_old_individual_id(
                    program=program,
                    old_individual_id=individual.copied_from_id,
                )
                for individual in old_selected_individuals
            ]
            selected_individuals = [individual for individual in selected_individuals if individual]
            needs_adjudication_ticket_copy.save()

            needs_adjudication_ticket_copy.possible_duplicates.set(possible_duplicates)
            needs_adjudication_ticket_copy.selected_individuals.set(selected_individuals)

        # Handle current program ticket
        needs_adjudication_ticket.ticket.programs.set([current_program])
        possible_duplicates = [
            get_individual_representation_per_program_by_old_individual_id(
                program=current_program,  # type: ignore
                old_individual_id=individual.copied_from_id,
            )
            for individual in individuals
        ]
        possible_duplicates = [individual for individual in possible_duplicates if individual]

        # Handle selected_individuals
        old_selected_individuals = needs_adjudication_ticket.selected_individuals.all()
        selected_individuals = [
            get_individual_representation_per_program_by_old_individual_id(
                program=current_program,  # type: ignore
                old_individual_id=individual.copied_from_id,
            )
            for individual in old_selected_individuals
        ]
        selected_individuals = [individual for individual in selected_individuals if individual]

        needs_adjudication_ticket.golden_records_individual = possible_duplicates.pop()
        needs_adjudication_ticket.save(update_fields=["golden_records_individual"])

        needs_adjudication_ticket.selected_individuals.set(selected_individuals)
        needs_adjudication_ticket.possible_duplicates.set(possible_duplicates)
        if hasattr(needs_adjudication_ticket, "role_reassign_data"):
            handle_role_reassign_data(needs_adjudication_ticket, current_program)  # type: ignore
        if hasattr(needs_adjudication_ticket, "extra_data"):
            handle_extra_data(needs_adjudication_ticket, current_program)  # type: ignore


def migrate_messages() -> None:
    print("Handle Messages")
    message_objects = (
        Message.objects.select_related(
            "target_population",
            "target_population__program",
        )
        .prefetch_related(
            "households",
            "households__copied_to",
        )
        .filter(program__isnull=True)
    )
    for message in message_objects.iterator():
        if message.target_population:
            program = message.target_population.program
            if message.households.exists():
                households_representations = [
                    get_household_representation_per_program_by_old_household_id(
                        program=program,
                        old_household_id=household.id,
                    )
                    for household in message.households.all().only("id")
                ]
                households_representations = [household for household in households_representations if household]
                message.households.set(households_representations)
            message.program_id = program
            message.save(update_fields=["program_id"])
        else:
            if message.households.exists():
                programs = list(message.households.values_list("copied_to__program", flat=True).distinct())

                current_program = programs.pop()

                for program in programs:
                    copy_message(message, program)

                # Handle current program ticket
                households_representations = [
                    get_household_representation_per_program_by_old_household_id(
                        program=current_program,
                        old_household_id=household.id,
                    )
                    for household in message.households.all().only("id")
                ]
                households_representations = [household for household in households_representations if household]
                message.households.set(households_representations)
                message.program_id = current_program
                message.save(update_fields=["program_id"])
        print("Handle Messages not connected to any program")
        handle_non_program_messages()


def copy_message(active_message: Message, program: Program) -> None:
    message = copy.deepcopy(active_message)
    message.pk = None
    message.unicef_id = None
    message.program_id = program
    message.save()

    households_representations = [
        get_household_representation_per_program_by_old_household_id(
            program=program,
            old_household_id=household.id,
        )
        for household in active_message.households.all().only("id")
    ]
    households_representations = [household for household in households_representations if household]
    message.households.set(households_representations)


def migrate_feedback() -> None:
    print("Handle Feedback objects")
    # Handle closed Feedback (Feedback related to a closed grievance ticket) OR Feedback with program
    assign_feedback_to_program()
    # Handle active Feedback objects without program -
    # (Feedback with active tickets OR Feedback not related to any ticket) AND without defined program
    handle_active_feedback()
    print("Handle Feedback not connected to any program")
    handle_non_program_feedback()


def assign_feedback_to_program() -> None:
    feedback_objects_for_specific_program = (
        Feedback.objects.select_related(
            "program",
            "household_lookup",
            "individual_lookup",
            "linked_grievance",
            "household_lookup__program",
            "individual_lookup__program",
        )
        .filter(Q(linked_grievance__status=GrievanceTicket.STATUS_CLOSED) | Q(program__isnull=False))
        .distinct()
    )
    for feedback_obj in feedback_objects_for_specific_program.iterator():
        if feedback_obj.program:
            program = feedback_obj.program
        elif feedback_obj.household_lookup:
            program = feedback_obj.household_lookup.program
        elif feedback_obj.individual_lookup:
            program = feedback_obj.individual_lookup.program
        else:
            program = None

        if feedback_obj.individual_lookup and feedback_obj.individual_lookup.program != program:
            individual_representation = get_individual_representation_per_program_by_old_individual_id(
                program=program,
                old_individual_id=feedback_obj.individual_lookup.copied_from_id,
            )
            feedback_obj.individual_lookup = individual_representation
        if feedback_obj.household_lookup and feedback_obj.household_lookup.program != program:
            household_representation = get_household_representation_per_program_by_old_household_id(
                program=program,
                old_household_id=feedback_obj.household_lookup.copied_from_id,
            )
            feedback_obj.household_lookup = household_representation
        if program:
            if feedback_obj.linked_grievance:
                feedback_obj.linked_grievance.programs.set([program])
            feedback_obj.program = program
            feedback_obj.save(update_fields=["program", "household_lookup", "individual_lookup"])


def handle_active_feedback() -> None:
    active_feedback_objects = (
        Feedback.objects.select_related(
            "linked_grievance",
            "program",
            "household_lookup",
            "individual_lookup",
            "household_lookup__program",
            "individual_lookup__program",
        )
        .prefetch_related(
            "feedback_messages",
        )
        .filter(
            (Q(linked_grievance__isnull=True) | ~Q(linked_grievance__status=GrievanceTicket.STATUS_CLOSED))
            & Q(program__isnull=True)
        )
        .distinct()
    )
    for feedback_obj in active_feedback_objects.iterator():
        current_program = None
        if feedback_obj.individual_lookup:
            individual_representations = feedback_obj.individual_lookup.copied_to.all()
            current_program = feedback_obj.individual_lookup.program
        else:
            individual_representations = Individual.objects.none()
        if feedback_obj.household_lookup:
            household_representations = feedback_obj.household_lookup.copied_to.all()
            current_program = feedback_obj.household_lookup.program
        else:
            household_representations = Household.objects.none()
        if current_program:
            household_programs = (
                household_representations.exclude(program=current_program).values_list("program", flat=True).distinct()
            )
            individual_programs = (
                individual_representations.exclude(program=current_program).values_list("program", flat=True).distinct()
            )

            all_programs = household_programs.union(individual_programs)

            for program in all_programs:
                copy_feedback(feedback_obj, program)
            # Handle current program feedback
            if feedback_obj.individual_lookup:
                individual_representation = get_individual_representation_per_program_by_old_individual_id(
                    program=current_program,
                    old_individual_id=feedback_obj.individual_lookup.copied_from_id,
                )
                feedback_obj.individual_lookup = individual_representation

            if feedback_obj.household_lookup:
                household_representation = get_household_representation_per_program_by_old_household_id(
                    program=current_program,
                    old_household_id=feedback_obj.household_lookup.copied_from_id,
                )
                feedback_obj.household_lookup = household_representation

            if feedback_obj.linked_grievance:
                feedback_obj.linked_grievance.programs.set([current_program])
            feedback_obj.program = current_program
            feedback_obj.save(update_fields=["program", "household_lookup", "individual_lookup"])


def copy_feedback(feedback_obj: Feedback, program: Program) -> None:
    feedback_copy = copy.deepcopy(feedback_obj)
    if feedback_copy.household_lookup:
        household_representation = get_household_representation_per_program_by_old_household_id(
            program=program,
            old_household_id=feedback_copy.household_lookup.copied_from_id,
        )
        feedback_copy.household_lookup = household_representation

    if feedback_copy.individual_lookup:
        individual_representation = get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=feedback_copy.individual_lookup.copied_from_id,
        )
        feedback_copy.individual_lookup = individual_representation

    feedback_copy.pk = None
    feedback_copy.unicef_id = None
    if feedback_copy.linked_grievance:
        feedback_copy = copy_grievance_ticket(
            feedback_copy, program, feedback_obj, related_grievance_field="linked_grievance"
        )

    feedback_copy.program_id = program
    feedback_copy.save()
    for message in feedback_obj.feedback_messages.all():
        message.pk = None
        message.feedback = feedback_copy
        message.save()


def copy_grievance_ticket(
    related_ticket: Any,
    program: Program,
    active_ticket: Any,
    related_grievance_field: str = "ticket",
) -> Any:
    grievance_ticket = getattr(related_ticket, related_grievance_field)
    original_grievance_ticket_id = grievance_ticket.pk
    grievance_ticket.pk = None
    grievance_ticket.unicef_id = None

    grievance_ticket.save()
    grievance_ticket.programs.set([program])
    grievance_ticket.linked_tickets.set(getattr(active_ticket, related_grievance_field).linked_tickets.distinct())
    grievance_ticket.linked_tickets.add(original_grievance_ticket_id)

    for note in getattr(active_ticket, related_grievance_field).ticket_notes.all():
        note.pk = None
        note.ticket = grievance_ticket
        note.save()

    for document in getattr(active_ticket, related_grievance_field).support_documents.all():
        document.pk = None
        document.grievance_ticket = grievance_ticket
        document.save()

    setattr(related_ticket, related_grievance_field, grievance_ticket)
    return related_ticket


def create_void_program(business_area: BusinessArea) -> Program:
    return Program.objects.get_or_create(
        name="Void Program",
        business_area=business_area,
        defaults=dict(
            status=Program.DRAFT,
            start_date=timezone.datetime.min,
            end_date=timezone.datetime.max,
            budget=0,
            frequency_of_payments=Program.ONE_OFF,
            sector=Program.CHILD_PROTECTION,
            scope=Program.SCOPE_FOR_PARTNERS,
            cash_plus=True,
            population_goal=1,
        ),
    )[0]


def handle_non_program_tickets() -> None:
    """
    Handle tickets that are not connected to any project. They should be moved to dummy program.
    """
    for business_area in BusinessArea.objects.all().iterator():
        non_program_query = Q(ticket__programs__isnull=True) & Q(ticket__business_area=business_area)
        non_program_tickets = chain(
            TicketComplaintDetails.objects.filter(non_program_query),
            TicketSensitiveDetails.objects.filter(non_program_query),
            TicketPaymentVerificationDetails.objects.filter(non_program_query),
            TicketHouseholdDataUpdateDetails.objects.filter(non_program_query),
            TicketIndividualDataUpdateDetails.objects.filter(non_program_query),
            TicketAddIndividualDetails.objects.filter(non_program_query),
            TicketDeleteIndividualDetails.objects.filter(non_program_query),
            TicketDeleteHouseholdDetails.objects.filter(non_program_query),
            TicketSystemFlaggingDetails.objects.filter(non_program_query),
            TicketPositiveFeedbackDetails.objects.filter(non_program_query),
            TicketNegativeFeedbackDetails.objects.filter(non_program_query),
            TicketNeedsAdjudicationDetails.objects.filter(non_program_query),
            TicketReferralDetails.objects.filter(non_program_query),
        )
        try:
            first = next(non_program_tickets)
        except StopIteration:
            return
        non_program_tickets = chain([first], non_program_tickets)

        void_program = create_void_program(business_area)
        through_model = GrievanceTicket.programs.through

        object_list = []
        counter = 0
        for non_program_ticket in non_program_tickets:
            object_list.append(
                through_model(grievanceticket_id=non_program_ticket.ticket_id, program_id=void_program.id)
            )
            counter += 1
            if counter == BATCH_SIZE:
                through_model.objects.bulk_create(object_list)
                counter = 0
                object_list = []
        if object_list:
            through_model.objects.bulk_create(object_list)


def handle_non_program_feedback() -> None:
    """
    Handle feedback that is not connected to any project. They should be moved to dummy program.
    """
    for business_area in BusinessArea.objects.all().iterator():
        non_program_feedback_objects = Feedback.objects.filter(Q(program__isnull=True) & Q(business_area=business_area))
        if non_program_feedback_objects:
            void_program = create_void_program(business_area)

            through_model = GrievanceTicket.programs.through
            object_list = []
            counter = 0
            for ticket_id in non_program_feedback_objects.filter(linked_grievance__isnull=False).values_list(
                "linked_grievance_id", flat=True
            ):
                object_list.append(through_model(grievanceticket_id=ticket_id, program_id=void_program.id))
                counter += 1

                if counter >= BATCH_SIZE:
                    through_model.objects.bulk_create(object_list)
                    counter = 0
                    object_list = []
            if object_list:
                through_model.objects.bulk_create(object_list)

            non_program_feedback_objects.update(program=void_program)


def handle_non_program_messages() -> None:
    for business_area in BusinessArea.objects.all().iterator():
        non_program_messages = Message.objects.filter(Q(program__isnull=True) & Q(business_area=business_area))
        if non_program_messages:
            void_program = create_void_program(business_area)
            non_program_messages.update(program=void_program)


def handle_role_reassign_data(ticket: Any, program: Program) -> Any:
    """
    role_reassign_data structure:
    {
        role_uuid / "HEAD": {
            "household": household_encoded_id,
            "individual": individual_encoded_id,
            "role": role
        },
        ...
    }
    """

    def retrieve_household_representation(household_from_json: Household, program: Program) -> Optional[Household]:
        if household_from_json_in_program := household_from_json.copied_to.filter(program=program).first():
            encoded_id = encode_id_base64(household_from_json_in_program.id, "Household")
            role_data["household"] = encoded_id
        return household_from_json_in_program

    def retrieve_individual_representation(individual_from_json: Individual, program: Program) -> Optional[Individual]:
        if individual_from_json_in_program := individual_from_json.copied_to.filter(program=program).first():
            encoded_id = encode_id_base64(individual_from_json_in_program.id, "Individual")
            role_data["individual"] = encoded_id
        return individual_from_json_in_program

    def retrieve_role_from_program(role_from_json: IndividualRoleInHousehold, program: Program) -> Optional[Individual]:
        role_household_in_program = role_from_json.household.copied_from.copied_to.filter(program=program).first()
        role_individual_in_program = role_from_json.individual.copied_from.copied_to.filter(program=program).first()

        role_from_json_in_program = IndividualRoleInHousehold.objects.filter(
            household=role_household_in_program, individual=role_individual_in_program
        ).first()
        return role_from_json_in_program

    if not ticket.role_reassign_data:
        return ticket

    new_role_reassign_data = {}
    for role_uuid, role_data in ticket.role_reassign_data.items():
        role_data_to_extend = {}

        household_from_json = Household.objects.filter(id=decode_id_string(role_data.get("household"))).first()
        # Fetch correct household representation from JSON
        household_from_json_in_program = (
            retrieve_household_representation(household_from_json, program) if household_from_json else None
        )

        individual_from_json = Individual.objects.filter(id=decode_id_string(role_data.get("individual"))).first()
        # Fetch correct individual representation from JSON
        individual_from_json_in_program = (
            retrieve_individual_representation(individual_from_json, program) if individual_from_json else None
        )

        if household_from_json_in_program and individual_from_json_in_program:
            if role_uuid == "HEAD":
                role_data_to_extend["HEAD"] = role_data
            else:
                role_from_json = IndividualRoleInHousehold.objects.filter(id=role_uuid).first()
                # Fetch correct role representation from JSON
                role_from_json_in_program = (
                    retrieve_role_from_program(role_from_json, program) if role_from_json else None
                )
                if role_from_json_in_program:
                    role_data_to_extend[str(role_from_json_in_program.id)] = role_data

        if role_data_to_extend:
            new_role_reassign_data.update(role_data_to_extend)

    ticket.role_reassign_data = new_role_reassign_data
    ticket.save(update_fields=["role_reassign_data"])
    return ticket


def handle_extra_data(ticket: Any, program: Program) -> Any:
    """
    extra_data structure:
    {
        "golden_records": [
            {
                "dob": date_of_birth,
                "full_name": full_name,
                "hit_id": hit_id,
                "location": location,
                "proximity_to_score": proximity_to_score,
                "score": score
            },
            ...
        ],
        "possible_duplicate": [
            {
                "dob": date_of_birth,
                "full_name": full_name,
                "hit_id":  hit_id,
                "location": location,
                "proximity_to_score": proximity_to_score,
                "score": score
            },
            ...
        ]
    }
    """

    if not ticket.extra_data:
        return ticket

    for list_data in ticket.extra_data.values():
        for ind_data in list_data:
            id_found = False
            hit_from_json = Individual.objects.filter(id=ind_data.get("hit_id")).first()
            # Fetch correct individual representation from JSON
            if hit_from_json:
                hit_from_json_in_program = hit_from_json.copied_to.filter(program=program).first()
                if hit_from_json_in_program:
                    id_found = True
                    ind_data["hit_id"] = str(hit_from_json_in_program.id)
            if id_found is False:
                list_data.remove(ind_data)

    ticket.save()
    return ticket


def handle_individual_data(
    ticket: TicketIndividualDataUpdateDetails, program: Program
) -> TicketIndividualDataUpdateDetails:
    """
    individual_data consists of multiple values, but only some have ids.
    These are: [documents/identities/payment_channels]_to_remove and _to_edit.
    Structure of individual_data:
    {
        "_to_remove": [
            {
                "approve_status": bool,
                "value": "base64_id_of_object_to_remove"
            }
        ]
        "_to_edit": [
            {
                "approve_status": bool,
                "previous_value": {
                    "id": base64_object_id,
                    (if not document)
                    "individual": base64_individual_id,
                    **other_object_specific_fields
                },
                "value": {
                    "id": base64_object_id(the same as the one above),
                    (if not document)
                    "individual": base64_individual_id,
                    **other_object_specific_fields
                }
            }
        ],
        also for _to_remove objects there are corresponding previous_[documents/identities/payment_channels].
        {
            "base64_object_id": {
                "id": same as base64_object_id(same as value in _to_remove),
                "individual" base64_document_individual_id,
                **object specific data
            }
        }
    }
    """
    individual = ticket.individual
    individual_in_program = individual.copied_to.filter(program=program).first()
    if not individual_in_program:
        return ticket

    encoded_individual_id = encode_id_base64(individual_in_program.id, "Individual")
    individual_data = ticket.individual_data
    if not individual_data:
        return ticket

    for model in (Document, IndividualIdentity, BankAccountInfo):
        IndividualDataObjectsToEditHandler(
            individual_data,
            individual_in_program,
            model,
            encoded_individual_id,
        ).handle_objects_to_edit()
        IndividualDataObjectsToRemoveHandler(
            individual_data,
            individual_in_program,
            model,
            encoded_individual_id,
        ).handle_objects_to_remove()

    ticket.individual_data = individual_data
    ticket.save(update_fields=["individual_data"])
    return ticket


class IndividualDataObjectsToRemoveHandler:
    def __init__(
        self,
        individual_data: dict,
        individual_in_program: Individual,
        model: Any,
        encoded_individual_id: Optional[str],
    ) -> None:
        self.individual_data = individual_data
        self.model = model
        self.objects_to_remove_string, self.previous_objects_string = self.object_specific_update_fields()
        self.individual_in_program = individual_in_program
        self.encoded_individual_id = encoded_individual_id

    def object_specific_update_fields(self) -> tuple[str, str]:
        model_related_string = {
            Document: "documents",
            IndividualIdentity: "identities",
            BankAccountInfo: "payment_channels",
        }[self.model]
        return f"{model_related_string}_to_remove", f"previous_{model_related_string}"

    def object_specific_get_fields(self, previous_object: dict) -> dict:
        if self.model == IndividualIdentity:
            return {
                "country__iso_code3": previous_object.get("country"),
                "number": previous_object.get("number"),
                "partner__name": previous_object.get("partner"),
            }
        elif self.model == Document:
            return {
                "document_number": previous_object.get("document_number"),
                "country__iso_code3": previous_object.get("country"),
                "type__key": previous_object.get("key"),
            }
        else:
            return {
                "bank_name": previous_object.get("bank_name"),
                "bank_account_number": previous_object.get("bank_account_number"),
            }

    def handle_individual_data_update(
        self,
        index: int,
        object_in_program_encoded_id: Optional[str],
        object_to_remove_id: str,
    ) -> None:
        self.individual_data[self.objects_to_remove_string][index]["value"] = object_in_program_encoded_id
        self.individual_data[self.previous_objects_string][object_to_remove_id]["id"] = object_in_program_encoded_id
        self.individual_data[self.previous_objects_string][object_to_remove_id][
            "individual"
        ] = self.encoded_individual_id
        if object_in_program_encoded_id != object_to_remove_id:
            self.individual_data[self.previous_objects_string][object_in_program_encoded_id] = copy.deepcopy(
                self.individual_data[self.previous_objects_string][object_to_remove_id]
            )
            del self.individual_data[self.previous_objects_string][object_to_remove_id]

    def handle_objects_to_remove(self) -> None:
        for index, object_to_remove in enumerate(self.individual_data.get(self.objects_to_remove_string, [])):
            object_to_remove_id = object_to_remove.get("value")
            previous_object = self.individual_data.get(self.previous_objects_string, {}).get(object_to_remove_id, {})
            if not previous_object:
                continue
            object_in_program = self.model.objects.filter(
                individual=self.individual_in_program,
                **self.object_specific_get_fields(previous_object),
            ).first()
            if object_in_program:
                object_in_program_encoded_id = encode_id_base64(object_in_program.id, self.model.__name__)
                self.handle_individual_data_update(
                    index,
                    object_in_program_encoded_id,
                    object_to_remove_id,
                )


class IndividualDataObjectsToEditHandler:
    def __init__(
        self,
        individual_data: dict,
        individual_in_program: Individual,
        model: Any,
        encoded_individual_id: Optional[str],
    ) -> None:
        self.individual_data = individual_data
        self.model = model
        self.objects_to_edit_string = self.object_specific_edit_fields()
        self.individual_in_program = individual_in_program
        self.encoded_individual_id = encoded_individual_id

    def object_specific_edit_fields(self) -> str:
        model_related_string = {
            Document: "documents",
            IndividualIdentity: "identities",
            BankAccountInfo: "payment_channels",
        }[self.model]
        return f"{model_related_string}_to_edit"

    def get_object_specific_fields(self, previous_value: dict) -> dict:
        if self.model == IndividualIdentity:
            return {
                "country__iso_code3": previous_value.get("country"),
                "number": previous_value.get("number"),
                "partner__name": previous_value.get("partner"),
            }
        elif self.model == Document:
            return {
                "document_number": previous_value.get("number"),
                "country__iso_code3": previous_value.get("country"),
            }
        else:
            return {
                "bank_name": previous_value.get("bank_name"),
                "bank_account_number": previous_value.get("bank_account_number"),
            }

    def handle_objects_to_edit(self) -> None:
        for index, object_to_edit in enumerate(self.individual_data.get(self.objects_to_edit_string, [])):
            object_in_program = self.model.objects.filter(
                individual=self.individual_in_program,
                **self.get_object_specific_fields(object_to_edit.get("previous_value", {})),
            ).first()
            if not object_in_program:
                object_in_program = self.model.objects.filter(
                    individual=self.individual_in_program,
                    **self.get_object_specific_fields(object_to_edit.get("value", {})),
                ).first()
                if not object_in_program:
                    continue
            object_in_program_encoded_id = encode_id_base64(object_in_program.id, self.model.__name__)
            self.individual_data[self.objects_to_edit_string][index]["value"]["id"] = object_in_program_encoded_id
            self.individual_data[self.objects_to_edit_string][index]["previous_value"][
                "id"
            ] = object_in_program_encoded_id
            if self.model != Document:
                self.individual_data[self.objects_to_edit_string][index]["value"][
                    "individual"
                ] = self.encoded_individual_id
                self.individual_data[self.objects_to_edit_string][index]["previous_value"][
                    "individual"
                ] = self.encoded_individual_id
