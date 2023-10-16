import csv
import logging
import os
from collections import defaultdict
from typing import Any, Dict, Optional

from django.db import transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.models import (
    BankAccountInfo,
    Document,
    EntitlementCard,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import Payment, PaymentRecord
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation

logger = logging.getLogger(__name__)

BATCH_SIZE = 100
BATCH_SIZE_SMALL = 20


def migrate_data_to_representations() -> None:
    apply_country_specific_rules()
    for business_area in BusinessArea.objects.all():
        logger.info("----- NEW BUSINESS AREA -----")
        logger.info(f"Handling business area: {business_area}")
        migrate_data_to_representations_per_business_area(business_area=business_area)

    apply_congo_withdrawal()


def migrate_data_to_representations_per_business_area(business_area: BusinessArea) -> None:
    """
    This function is used to migrate data from old models to new representations per business_area.
    Take TargetPopulations:
    - all for programs in status ACTIVE
    - in status STATUS_READY_FOR_PAYMENT_MODULE and STATUS_READY_FOR_CASH_ASSIST for programs in status FINISHED,
    delete other TargetPopulations
    For all households and individuals in given TargetPopulations:
    - create new representations
    - copy all objects related to old households/individuals or adjust existing ones if they are related to program
    - handle RDI: if there is RDI for household copy all households in this RDI to current program
    For whole business_area:
    - for rdi that was not related to program: add rdi and copy its households to the biggest program in that ba
    - adjust payments and payment_records to corresponding representations

    """
    hhs_to_ignore = get_ignored_hhs() if business_area.name == "Afghanistan" else None
    for program in Program.objects.filter(
        business_area=business_area, status__in=[Program.ACTIVE, Program.FINISHED]
    ).order_by("status"):
        logger.info("----- NEW PROGRAM -----")
        logger.info(f"Creating representations for program: {program}")
        target_populations_ids = TargetPopulation.objects.filter(
            program=program,
        ).values_list("id", flat=True)

        household_selections = HouseholdSelection.original_and_repr_objects.filter(
            Q(target_population_id__in=target_populations_ids)
            & Q(is_original=True)
            & Q(is_migration_handled=False)
            & (
                Q(
                    target_population__status__in=[
                        TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE,
                        TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
                    ]
                )
                | Q(household__withdrawn=False)
            )
        )
        household_ids = household_selections.distinct("household").values_list("household_id", flat=True)

        if program.status == Program.ACTIVE:
            households_with_compatible_collection_type = Household.original_and_repr_objects.filter(
                is_original=True,
                is_migration_handled=False,
                data_collecting_type__in=program.data_collecting_type.compatible_types.all(),
                withdrawn=False,
                business_area=business_area,
            ).only("id")
            if hhs_to_ignore:
                households_with_compatible_collection_type = households_with_compatible_collection_type.exclude(
                    id__in=hhs_to_ignore
                )
            households = Household.original_and_repr_objects.filter(
                Q(id__in=household_ids) | Q(id__in=households_with_compatible_collection_type)
            ).filter(is_migration_handled=False, is_original=True)
        else:
            households = Household.original_and_repr_objects.filter(
                id__in=household_ids, is_migration_handled=False, is_original=True
            )
        households_count = households.count()

        logger.info(f"Handling households for program: {program}")

        for batch_start in range(0, households_count, BATCH_SIZE):
            batch_end = batch_start + BATCH_SIZE
            logger.info(f"Handling {batch_start} - {batch_end}/{households_count} households")
            individuals_per_household_dict = defaultdict(list)
            batched_households = households[batch_start:batch_end]
            for individual in Individual.objects.filter(household__in=batched_households):
                individuals_per_household_dict[individual.household_id].append(individual)
            for household in batched_households:
                with transaction.atomic():
                    copy_household_representation(household, program, individuals_per_household_dict[household.id])

        rdi_ids = households.values_list("registration_data_import_id", flat=True).distinct()
        rdis = RegistrationDataImport.objects.filter(id__in=rdi_ids)
        if program.status == Program.ACTIVE:
            logger.info(f"Handling RDIs for program: {program}")
            handle_rdis(rdis, program, hhs_to_ignore)
        else:
            rdi_through = RegistrationDataImport.programs.through
            rdi_through.objects.bulk_create(
                [rdi_through(registrationdataimport_id=rdi.id, program_id=program.id) for rdi in rdis],
                ignore_conflicts=True,
            )

        logger.info(f"Copying roles for program: {program}")
        copy_roles(households, program=program)

        logger.info(f"Copying household selections for program: {program}")
        copy_household_selections(household_selections, program)

        logger.info(f"Finished creating representations for program: {program}")

    Household.original_and_repr_objects.filter(
        business_area=business_area, copied_to__isnull=False, is_original=True
    ).distinct().update(is_migration_handled=True)
    logger.info("Handling objects without any representations yet - enrolling to storage programs")
    copy_non_program_objects_to_void_storage_programs(business_area, hhs_to_ignore)

    # logger.info("Adjusting payments and payment records")
    # adjust_payments(business_area)
    # adjust_payment_records(business_area)


def get_household_representation_per_program_by_old_household_id(
    program: Program,
    old_household_id: str,
) -> Optional[Household]:
    return Household.original_and_repr_objects.filter(
        program=program,
        copied_from_id=old_household_id,
        is_original=False,
    ).first()


def get_individual_representation_per_program_by_old_individual_id(
    program: Program,
    old_individual_id: str,
) -> Optional[Individual]:
    return Individual.original_and_repr_objects.filter(
        program=program,
        copied_from_id=old_individual_id,
        is_original=False,
    ).first()


def copy_household_representation(
    household: Household,
    program: Program,
    individuals: list[Individual],
) -> Optional[Household]:
    """
    Copy household into representation for given program if it does not exist yet.
    """
    # copy representations only based on original households
    if household.is_original:
        # if there is no representation of this household in this program yet, copy the household
        if household_representation := Household.original_and_repr_objects.filter(
            program=program,
            copied_from=household,
            is_original=False,
        ).first():
            return household_representation
        else:
            return copy_household(household, program, individuals)
    return household


def copy_household(household: Household, program: Program, individuals: list[Individual]) -> Household:
    original_household_id = household.id
    original_head_of_household_id = household.head_of_household.pk
    household.copied_from_id = original_household_id
    household.origin_unicef_id = household.unicef_id
    household.pk = None
    household.unicef_id = None
    household.program = program
    household.is_original = False

    # original_household = Household.original_and_repr_objects.get(pk=original_household_id)

    individuals_to_create = []
    for individual in individuals:
        individuals_to_create.append(copy_individual_representation(program, individual))

    household.head_of_household = get_individual_representation_per_program_by_old_individual_id(
        program=program,
        old_individual_id=original_head_of_household_id,
    )

    household.save()
    for individual in individuals_to_create:  # type: ignore
        individual.household = household

    Individual.original_and_repr_objects.bulk_update(individuals_to_create, ["household"])

    # copy_entitlement_card_per_household(household=original_household, household_representation=household)

    del individuals_to_create
    return household


def copy_individual_representation(
    program: Program,
    individual: Individual,
) -> Optional[Individual]:
    """
    Copy individual into representation for given program if it does not exist yet.
    Return existing representation if it exists.
    """
    # copy representations only based on original individuals
    if individual.is_original:
        # if there is no representation of this individual in this program yet, copy the individual
        if individual_representation := get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=individual.pk,
        ):
            return individual_representation
        else:
            return copy_individual(individual, program)
    else:
        return get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=individual.copied_from.pk,
        )


def copy_individual(individual: Individual, program: Program) -> Individual:
    original_individual_id = individual.id
    individual.copied_from_id = original_individual_id
    individual.origin_unicef_id = individual.unicef_id
    individual.pk = None
    individual.unicef_id = None
    individual.program = program
    individual.household = None
    individual.is_original = False
    individual.save()
    individual.refresh_from_db()

    original_individual = Individual.original_and_repr_objects.get(pk=original_individual_id)

    copy_document_per_individual(original_individual, individual)
    copy_individual_identity_per_individual(original_individual, individual)
    copy_bank_account_info_per_individual(original_individual, individual)

    return individual


def copy_roles(households: QuerySet, program: Program) -> None:
    # filter only original roles
    roles = (
        IndividualRoleInHousehold.original_and_repr_objects.filter(
            household__in=households,
            individual__is_removed=False,
            household__is_removed=False,
            is_original=True,
        )
        .exclude(copied_to__household__program=program)
        .order_by("pk")
    )

    roles_count = roles.count()
    for batch_start in range(0, roles_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logger.info(f"Handling {batch_start} - {batch_end}/{roles_count} roles")
        roles_list = []
        for role in roles[0:BATCH_SIZE]:
            household_representation = get_household_representation_per_program_by_old_household_id(
                program=program,
                old_household_id=role.household_id,
            )
            individual_representation = get_individual_representation_per_program_by_old_individual_id(
                program=program,
                old_individual_id=role.individual_id,
            )
            if not individual_representation:
                individual_representation = copy_individual_representation(program=program, individual=role.individual)

            original_role_id = role.id
            role.copied_from_id = original_role_id
            role.pk = None
            role.household = household_representation
            role.individual = individual_representation
            role.is_original = False
            roles_list.append(role)

        IndividualRoleInHousehold.original_and_repr_objects.bulk_create(roles_list)
        del roles_list


def copy_entitlement_card_per_household(household: Household, household_representation: Household) -> None:
    entitlement_cards = household.entitlement_cards.all()
    entitlement_cards_list = []
    for entitlement_card in entitlement_cards:
        original_entitlement_card_id = entitlement_card.id
        entitlement_card.copied_from_id = original_entitlement_card_id
        entitlement_card.pk = None
        entitlement_card.household = household_representation
        entitlement_card.is_original = False
        entitlement_cards_list.append(entitlement_card)
    EntitlementCard.original_and_repr_objects.bulk_create(entitlement_cards_list)
    del entitlement_cards_list


def copy_document_per_individual(individual: Individual, individual_representation: Individual) -> None:
    """
    Clone document for individual if new individual_representation has been created.
    """
    documents = individual.documents.all()
    documents_list = []
    for document in documents:
        original_document_id = document.id
        document.copied_from_id = original_document_id
        document.pk = None
        document.individual = individual_representation
        document.program = individual_representation.program
        document.is_original = False
        documents_list.append(document)
    Document.original_and_repr_objects.bulk_create(documents_list)
    del documents_list


def copy_individual_identity_per_individual(individual: Individual, individual_representation: Individual) -> None:
    """
    Clone individual_identity for individual if new individual_representation has been created.
    """
    identities = individual.identities.all()
    identities_list = []
    for identity in identities:
        original_identity_id = identity.id
        identity.copied_from_id = original_identity_id
        identity.pk = None
        identity.individual = individual_representation
        identity.is_original = False
        identities_list.append(identity)
    IndividualIdentity.original_and_repr_objects.bulk_create(identities_list)
    del identities_list


def copy_bank_account_info_per_individual(individual: Individual, individual_representation: Individual) -> None:
    """
    Clone bank_account_info for individual if new individual_representation has been created.
    """
    bank_accounts_info = individual.bank_account_info.all()
    bank_accounts_info_list = []
    for bank_account_info in bank_accounts_info:
        original_bank_account_info_id = bank_account_info.id
        bank_account_info.copied_from_id = original_bank_account_info_id
        bank_account_info.pk = None
        bank_account_info.individual = individual_representation
        bank_account_info.is_original = False
        bank_accounts_info_list.append(bank_account_info)
    BankAccountInfo.original_and_repr_objects.bulk_create(bank_accounts_info_list)
    del bank_accounts_info_list


def copy_household_selections(household_selections: QuerySet, program: Program) -> None:
    """
    Copy HouseholdSelections to new households representations. By this TargetPopulations are adjusted.
    Because TargetPopulation is per program, HouseholdSelections are per program.
    """
    household_selections = household_selections.order_by("id")

    household_selection_count = household_selections.count()
    for _ in range(0, household_selection_count, BATCH_SIZE):
        household_selections_to_create = []
        batched_household_selections = household_selections[0:BATCH_SIZE]

        for household_selection in batched_household_selections:
            household_representation = get_household_representation_per_program_by_old_household_id(
                program.pk, household_selection.household_id
            )
            household_selection.pk = None
            household_selection.household = household_representation
            household_selection.is_original = False
            household_selections_to_create.append(household_selection)

        with transaction.atomic():
            HouseholdSelection.original_and_repr_objects.bulk_create(household_selections_to_create)
            HouseholdSelection.objects.filter(id__in=batched_household_selections.values_list("id", flat=True)).update(
                is_migration_handled=True
            )


def adjust_payments(business_area: BusinessArea) -> None:
    """
    Adjust payment individuals and households to their representations.
    Payment is already related to program through PaymentPlan (parent), and then TargetPopulation.
    """

    payments = Payment.objects.filter(
        parent__target_population__program__business_area=business_area, household__is_original=True
    ).order_by("pk")
    payments_count = payments.count()

    for batch_start in range(0, payments_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logger.info(f"Adjusting payments {batch_start} - {batch_end}/{payments_count}")
        payment_updates = []

        for payment in payments[0:BATCH_SIZE]:
            payment_program = payment.parent.target_population.program
            representation_collector = get_individual_representation_per_program_by_old_individual_id(
                program=payment_program,
                old_individual_id=payment.collector.pk,
            )
            if not representation_collector:
                representation_collector = copy_individual_representation(
                    program=payment_program, individual=payment.collector
                )
            # payment.head_of_household can be None
            if payment.head_of_household:
                representation_head_of_household = get_individual_representation_per_program_by_old_individual_id(
                    program=payment_program,
                    old_individual_id=payment.head_of_household.pk,
                )
            else:
                representation_head_of_household = None
            representation_household = get_household_representation_per_program_by_old_household_id(
                program=payment_program,
                old_household_id=payment.household_id,
            )
            payment.refresh_from_db()
            if representation_collector and representation_household:
                payment.collector = representation_collector
                payment.head_of_household = representation_head_of_household
                payment.household = representation_household
                payment_updates.append(payment)

        Payment.objects.bulk_update(payment_updates, fields=["collector_id", "head_of_household_id", "household_id"])
        del payment_updates


def adjust_payment_records(business_area: BusinessArea) -> None:
    """
    Adjust PaymentRecord individuals and households to their representations.
    PaymentRecord is already related to program through TargetPopulation.
    """
    payment_records = PaymentRecord.original_and_repr_objects.filter(
        target_population__program__business_area=business_area, household__is_original=True
    ).order_by("pk")
    payment_records_count = payment_records.count()
    for batch_start in range(0, payment_records_count, BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logger.info(f"Adjusting payment records {batch_start} - {batch_end}/{payment_records_count}")
        payment_record_updates = []

        for payment_record in payment_records[0:BATCH_SIZE]:
            payment_record_program = payment_record.target_population.program
            if payment_record.head_of_household:
                representation_head_of_household = get_individual_representation_per_program_by_old_individual_id(
                    program=payment_record_program,
                    old_individual_id=payment_record.head_of_household.pk,
                )
            else:
                representation_head_of_household = None
            representation_household = get_household_representation_per_program_by_old_household_id(
                program=payment_record_program,
                old_household_id=payment_record.household_id,
            )
            payment_record.refresh_from_db()
            if representation_household:
                payment_record.head_of_household = representation_head_of_household
                payment_record.household = representation_household
                payment_record_updates.append(payment_record)

        PaymentRecord.original_and_repr_objects.bulk_update(
            payment_record_updates, fields=["head_of_household_id", "household_id"]
        )
        del payment_record_updates


def handle_rdis(rdis: QuerySet, program: Program, hhs_to_ignore: Optional[QuerySet] = None) -> None:
    rdis_count = rdis.count()
    for i, rdi in enumerate(rdis):
        if i % 100 == 0:
            logger.info(f"Handling {i} - {i+99}/{rdis_count} RDIs")
        rdi_households = rdi.households.filter(is_original=True, withdrawn=False)
        if hhs_to_ignore:
            rdi_households = rdi_households.exclude(id__in=hhs_to_ignore)
        household_count = rdi_households.count()
        for batch_start in range(0, household_count, BATCH_SIZE_SMALL):
            batch_end = batch_start + BATCH_SIZE_SMALL
            logger.info(f"Copying {batch_start} - {batch_end}/{household_count} households for RDI")
            household_dict = {}
            with transaction.atomic():
                individuals_per_household_dict = defaultdict(list)
                batched_households = rdi_households[batch_start:batch_end]
                for individual in Individual.objects.filter(household__in=batched_households):
                    individuals_per_household_dict[individual.household_id].append(individual)
                for household in batched_households:
                    household_original_id = household.pk
                    household_representation = copy_household_representation(
                        household,
                        program,
                        individuals_per_household_dict[household_original_id],
                    )
                    household_dict[household_original_id] = household_representation

                copy_roles_from_dict(household_dict, program)  # type: ignore

        rdi.programs.add(program)


def copy_non_program_objects_to_void_storage_programs(
    business_area: BusinessArea, hhs_to_ignore: Optional[QuerySet] = None
) -> None:
    households = Household.original_and_repr_objects.filter(
        business_area=business_area, copied_to__isnull=True, is_original=True
    ).order_by("pk")
    if hhs_to_ignore:
        households = households.exclude(id__in=hhs_to_ignore)
    collecting_types = DataCollectingType.objects.filter(
        id__in=households.values_list("data_collecting_type", flat=True).distinct().order_by("pk")
    )

    for collecting_type in collecting_types:
        program = create_storage_program_for_collecting_type(business_area, collecting_type)
        households_with_collecting_type = households.filter(data_collecting_type=collecting_type)

        # Handle rdis before copying households so households query is not changed yet
        rdis = (
            RegistrationDataImport.objects.filter(
                households__in=households_with_collecting_type,
            )
            .distinct()
            .only("id")
        )
        rdi_through = RegistrationDataImport.programs.through
        rdi_through.objects.bulk_create(
            [rdi_through(registrationdataimport_id=rdi.id, program_id=program.id) for rdi in rdis],
            ignore_conflicts=True,
        )

        household_count = households_with_collecting_type.count()
        for batch_start in range(0, household_count, BATCH_SIZE_SMALL):
            batch_end = batch_start + BATCH_SIZE_SMALL
            logger.info(
                f"Copying {batch_start} - {batch_end}/{household_count} "
                f"households to program with collecting type {collecting_type}"
            )
            household_dict = {}
            with transaction.atomic():
                individuals_per_household_dict = defaultdict(list)
                batched_households = households_with_collecting_type[0:BATCH_SIZE_SMALL]
                for individual in Individual.objects.filter(household__in=batched_households):
                    individuals_per_household_dict[individual.household_id].append(individual)
                for household in batched_households:
                    household_original_id = household.pk
                    household_representation = copy_household(
                        household,
                        program,
                        individuals_per_household_dict[household_original_id],
                    )
                    household_dict[household_original_id] = household_representation

                copy_roles_from_dict(household_dict, program)


def copy_roles_from_dict(household_dict: dict[Any, Household], program: Program) -> None:
    roles = (
        IndividualRoleInHousehold.original_and_repr_objects.filter(
            household__id__in=household_dict.keys(),
            individual__is_removed=False,
            household__is_removed=False,
            is_original=True,
        )
        .exclude(copied_to__household__program=program)
        .order_by("pk")
    )

    roles_to_create = []
    for role in roles:
        household_representation = household_dict[role.household.pk]
        individual_representation = get_individual_representation_per_program_by_old_individual_id(
            program=program,
            old_individual_id=role.individual_id,
        )
        if not individual_representation:
            individual_representation = copy_individual_representation(program=program, individual=role.individual)

        original_role_id = role.id
        role.copied_from_id = original_role_id
        role.pk = None
        role.household = household_representation
        role.individual = individual_representation
        role.is_original = False
        roles_to_create.append(role)

    IndividualRoleInHousehold.original_and_repr_objects.bulk_create(roles_to_create)


def create_storage_program_for_collecting_type(
    business_area: BusinessArea, collecting_type: DataCollectingType
) -> Program:
    return Program.all_objects.get_or_create(
        name=f"Storage program - COLLECTION TYPE {collecting_type.label}",
        data_collecting_type=collecting_type,
        status=Program.DRAFT,
        start_date=timezone.now(),
        end_date=timezone.datetime.max,
        business_area=business_area,
        budget=0,
        frequency_of_payments=Program.ONE_OFF,
        sector=Program.CHILD_PROTECTION,
        scope=Program.SCOPE_FOR_PARTNERS,
        cash_plus=True,
        population_goal=1,
        is_removed=True,  # soft-deleted
    )[0]


def apply_country_specific_rules() -> None:
    apply_congo_rules()
    apply_sudan_rules()


def apply_congo_rules() -> None:
    logger.info("Applying Congo custom rules")

    business_area_congo = BusinessArea.objects.get(name="Democratic Republic of Congo")
    csv_congo_programs = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "files",
        "data_migration_gpf",
        "congo_rdi_program_untargetted.csv",
    )
    congo_dict = prepare_program_rdi_dict(csv_congo_programs, business_area_congo)

    for program in congo_dict:
        rdis = congo_dict[program]
        untargetted_hhs = Household.objects.filter(
            selections__isnull=True,
            registration_data_import__in=rdis,
        ).distinct()

        individuals_per_household_dict = defaultdict(list)
        for individual in Individual.objects.filter(household__in=untargetted_hhs):
            individuals_per_household_dict[individual.household_id].append(individual)
        for household in untargetted_hhs:
            with transaction.atomic():
                copy_household_representation(household, program, individuals_per_household_dict[household.id])

        rdi_through = RegistrationDataImport.programs.through
        rdi_through.objects.bulk_create(
            [rdi_through(registrationdataimport_id=rdi.id, program_id=program.id) for rdi in rdis],
            ignore_conflicts=True,
        )
        copy_roles(untargetted_hhs, program=program)

    logger.info("Finished applying Congo custom rules")


def apply_sudan_rules() -> None:
    logger.info("Applying Sudan custom rules")

    business_area_sudan = BusinessArea.objects.get(name="Sudan")
    csv_sudan_programs = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "files",
        "data_migration_gpf",
        "sudan_rdi_program.csv",
    )
    sudan_dict = prepare_program_rdi_dict(csv_sudan_programs, business_area_sudan)
    for program in sudan_dict:
        rdis = RegistrationDataImport.objects.filter(
            id__in=[rdi.id for rdi in sudan_dict[program]],
        )
        handle_rdis(rdis, program)


def prepare_program_rdi_dict(csv_rdi_program: str, business_area: BusinessArea) -> Dict:
    program_rdi_dict = {}
    with open(csv_rdi_program, mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        next(reader)
        for row in reader:
            program = Program.objects.filter(name=row[1], business_area=business_area).first()
            rdi = RegistrationDataImport.objects.filter(name=row[0], business_area=business_area).first()
            if rdi and program:
                if program in program_rdi_dict:
                    program_rdi_dict[program].append(rdi)
                else:
                    program_rdi_dict[program] = [rdi]
    return program_rdi_dict


def apply_congo_withdrawal() -> None:
    logger.info("Applying Congo custom withdrawal rules")
    business_area_congo = BusinessArea.objects.get(name="Democratic Republic of Congo")
    csv_congo_withdraw = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "files",
        "data_migration_gpf",
        "congo_to_withdraw.csv",
    )
    rdis_names = []
    with open(csv_congo_withdraw, mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            rdis_names.append(row[0])
    untargetted_hhs = (
        Household.objects.filter(
            selections__isnull=True,
            registration_data_import__name__in=rdis_names,
            registration_data_import__business_area=business_area_congo,
        )
        .only("id")
        .distinct()
    )
    Household.original_and_repr_objects.filter(copied_from__id__in=untargetted_hhs).update(withdrawn=True)


def get_ignored_hhs() -> QuerySet:
    business_area_afg = BusinessArea.objects.get(name="Afghanistan")
    csv_afg_ignore = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "files",
        "data_migration_gpf",
        "afg_to_ignore.csv",
    )
    rdis_names = []
    with open(csv_afg_ignore, mode="r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            rdis_names.append(row[0])

    return Household.objects.filter(
        selections__isnull=True,
        registration_data_import__name__in=rdis_names,
        registration_data_import__business_area=business_area_afg,
    ).values_list("id", flat=True)
