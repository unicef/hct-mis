from typing import List

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.utils import (
    decode_and_get_object,
    decode_and_get_object_required,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.payment.models import PaymentRecord


def create_tickets_based_on_payment_records_service(grievance_ticket, details, model) -> List[GrievanceTicket]:
    individual_encoded_id = details.get("individual")
    individual = decode_and_get_object(individual_encoded_id, Individual)

    household_encoded_id = details.get("household")
    household = decode_and_get_object(household_encoded_id, Household)

    payment_record_encoded_ids_list = details.get("payment_record") or []

    payment_record = None
    if payment_record_encoded_ids_list:
        payment_record_encoded_id = payment_record_encoded_ids_list.pop(0)
        payment_record = decode_and_get_object(payment_record_encoded_id, PaymentRecord)

    model.objects.create(
        individual=individual,
        household=household,
        payment_record=payment_record,
        ticket=grievance_ticket,
    )
    grievance_ticket.refresh_from_db()
    grievance_tickets_to_return = [grievance_ticket]

    for payment_record_encoded_id in payment_record_encoded_ids_list:
        payment_record = decode_and_get_object(payment_record_encoded_id, PaymentRecord)

        # copy GrievanceTicket object and assign linked tickets
        ticket = grievance_ticket
        linked_tickets = grievance_ticket.linked_tickets.all()
        ticket.pk = None
        ticket.save()
        ticket.linked_tickets.set(linked_tickets)

        model.objects.create(
            individual=individual,
            household=household,
            payment_record=payment_record,
            ticket=ticket,
        )

        ticket.refresh_from_db()
        grievance_tickets_to_return.append(ticket)

    return grievance_tickets_to_return


def update_ticket_based_on_payment_record_service(grievance_ticket, extras, input_data) -> GrievanceTicket:
    ticket_details = grievance_ticket.ticket_details

    if household_id := input_data.get("household"):
        household = decode_and_get_object_required(household_id, Household)
        if ticket_details.household and ticket_details.household != household:
            raise ValidationError("Cannot change household")
        ticket_details.household = household

    if individual_id := input_data.get("individual"):
        individual = decode_and_get_object_required(individual_id, Individual)
        if ticket_details.individual and ticket_details.individual != individual:
            raise ValidationError("Cannot change individual")
        ticket_details.individual = individual

    if payment_record_id := input_data.get("payment_record"):
        payment_record = decode_and_get_object_required(payment_record_id, PaymentRecord)
        ticket_details.payment_record = payment_record
    ticket_details.save()
    return grievance_ticket
