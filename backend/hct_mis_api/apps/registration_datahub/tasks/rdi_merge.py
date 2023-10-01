import contextlib
import logging
from typing import Dict, List, Tuple

from django.core.cache import cache
from django.db import transaction
from django.forms import model_to_dict

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.geo.models import Area, Country
from hct_mis_api.apps.grievance.services.needs_adjudication_ticket_services import (
    create_needs_adjudication_tickets,
)
from hct_mis_api.apps.household.celery_tasks import recalculate_population_fields_task
from hct_mis_api.apps.household.documents import HouseholdDocument, get_individual_doc
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    HEAD,
    NEEDS_ADJUDICATION,
    BankAccountInfo,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.celery_tasks import deduplicate_documents
from hct_mis_api.apps.registration_datahub.documents import get_imported_individual_doc
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualRoleInHousehold,
    KoboImportedSubmission,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    CheckAgainstSanctionListPreMergeTask,
)
from hct_mis_api.apps.utils.elasticsearch_utils import (
    populate_index,
    remove_elasticsearch_documents_by_matching_ids,
)
from hct_mis_api.apps.utils.phone import is_valid_phone_number
from hct_mis_api.apps.utils.querysets import evaluate_qs

logger = logging.getLogger(__name__)


class RdiMergeTask:
    HOUSEHOLD_FIELDS = (
        "consent_sign",
        "consent",
        "consent_sharing",
        "residence_status",
        "country_origin",
        "zip_code",
        "size",
        "address",
        "country",
        "female_age_group_0_5_count",
        "female_age_group_6_11_count",
        "female_age_group_12_17_count",
        "female_age_group_18_59_count",
        "female_age_group_60_count",
        "pregnant_count",
        "male_age_group_0_5_count",
        "male_age_group_6_11_count",
        "male_age_group_12_17_count",
        "male_age_group_18_59_count",
        "male_age_group_60_count",
        "female_age_group_0_5_disabled_count",
        "female_age_group_6_11_disabled_count",
        "female_age_group_12_17_disabled_count",
        "female_age_group_18_59_disabled_count",
        "female_age_group_60_disabled_count",
        "male_age_group_0_5_disabled_count",
        "male_age_group_6_11_disabled_count",
        "male_age_group_12_17_disabled_count",
        "male_age_group_18_59_disabled_count",
        "male_age_group_60_disabled_count",
        "first_registration_date",
        "last_registration_date",
        "flex_fields",
        "start",
        "deviceid",
        "name_enumerator",
        "org_enumerator",
        "org_name_enumerator",
        "village",
        "registration_method",
        "collect_individual_data",
        "currency",
        "unhcr_id",
        "geopoint",
        "returnee",
        "fchild_hoh",
        "child_hoh",
        "kobo_asset_id",
        "row_id",
        "data_collecting_type_id",
    )

    INDIVIDUAL_FIELDS = (
        "id",
        "photo",
        "full_name",
        "given_name",
        "middle_name",
        "family_name",
        "relationship",
        "sex",
        "birth_date",
        "estimated_birth_date",
        "marital_status",
        "phone_no",
        "phone_no_alternative",
        "email",
        "disability",
        "flex_fields",
        "first_registration_date",
        "last_registration_date",
        "deduplication_batch_status",
        "deduplication_batch_results",
        "observed_disability",
        "seeing_disability",
        "hearing_disability",
        "physical_disability",
        "memory_disability",
        "selfcare_disability",
        "comms_disability",
        "who_answers_phone",
        "who_answers_alt_phone",
        "pregnant",
        "work_status",
        "kobo_asset_id",
        "row_id",
        "disability_certificate_picture",
        "preferred_language",
        "age_at_registration",
    )

    def merge_admin_areas(
        self,
        imported_household: ImportedHousehold,
        household: Household,
    ) -> None:
        admins = {
            "admin_area": imported_household.admin_area,
            "admin1": imported_household.admin1,
            "admin2": imported_household.admin2,
            "admin3": imported_household.admin3,
            "admin4": imported_household.admin4,
        }

        for admin_key, admin_value in admins.items():
            if admin_value:
                admin_area = Area.objects.filter(p_code=admin_value).first()
                if admin_area:
                    setattr(household, admin_key, admin_area)
                else:
                    logger.exception(f"Provided {admin_key} {admin_value} does not exist")

        if household.admin_area:
            household.set_admin_areas(save=False)

    def _prepare_households(
        self, imported_households: List[ImportedHousehold], obj_hct: RegistrationDataImport
    ) -> Dict[int, Household]:
        households_dict = {}
        countries = {}
        for imported_household in imported_households:
            household_data = {**model_to_dict(imported_household, fields=self.HOUSEHOLD_FIELDS)}
            country = household_data.pop("country")
            country_origin = household_data.pop("country_origin")

            if country and country.code not in countries:
                countries[country.code] = Country.objects.get(iso_code2=country.code)
            if country_origin and country_origin.code not in countries:
                countries[country_origin.code] = Country.objects.get(iso_code2=country_origin.code)

            if country := countries.get(country.code):
                household_data["country"] = country

            if country_origin := countries.get(country_origin.code):
                household_data["country_origin"] = country_origin

            if record := imported_household.flex_registrations_record:
                household_data["registration_id"] = record.registration

            if enumerator_rec_id := imported_household.enumerator_rec_id:
                household_data["flex_fields"].update({"enumerator_id": enumerator_rec_id})

            household = Household(
                **household_data,
                registration_data_import=obj_hct,
                business_area=obj_hct.business_area,
            )
            self.merge_admin_areas(imported_household, household)
            households_dict[imported_household.id] = household

        return households_dict

    def _prepare_individual_documents_and_identities(
        self, imported_individual: ImportedIndividual, individual: Individual
    ) -> Tuple[List, List]:
        documents_to_create = []
        for imported_document in imported_individual.documents.all():
            document_type = DocumentType.objects.get(
                key=imported_document.type.key,
            )
            document = Document(
                document_number=imported_document.document_number,
                country=Country.objects.get(iso_code2=str(imported_document.country)),
                type=document_type,
                individual=individual,
                photo=imported_document.photo,
                expiry_date=imported_document.expiry_date,
                issuance_date=imported_document.issuance_date,
            )
            documents_to_create.append(document)
        identities_to_create = []
        for imported_identity in imported_individual.identities.all():
            partner, _ = Partner.objects.get_or_create(name=imported_identity.partner, defaults={"is_un": True})
            identity = IndividualIdentity(
                partner=partner,
                number=imported_identity.document_number,
                individual=individual,
                country=Country.objects.get(iso_code2=str(imported_identity.country)),
            )
            identities_to_create.append(identity)

        return documents_to_create, identities_to_create

    def _prepare_individuals(
        self,
        imported_individuals: List[ImportedIndividual],
        households_dict: Dict[int, Household],
        obj_hct: RegistrationDataImport,
    ) -> Tuple[Dict, List, List]:
        individuals_dict = {}
        documents_to_create = []
        identities_to_create = []
        for imported_individual in imported_individuals:
            values = model_to_dict(imported_individual, fields=self.INDIVIDUAL_FIELDS)

            if not values.get("phone_no_valid"):
                values["phone_no_valid"] = False
            if not values.get("phone_no_alternative_valid"):
                values["phone_no_alternative_valid"] = False

            imported_individual_household = imported_individual.household
            household = households_dict.get(imported_individual.household.id) if imported_individual_household else None

            phone_no = values.get("phone_no")
            phone_no_alternative = values.get("phone_no_alternative")

            values["phone_no_valid"] = is_valid_phone_number(str(phone_no))
            values["phone_no_alternative_valid"] = is_valid_phone_number(str(phone_no_alternative))

            individual = Individual(
                **values,
                household=household,
                registration_id=household.registration_id,
                business_area=obj_hct.business_area,
                registration_data_import=obj_hct,
                imported_individual_id=imported_individual.id,
            )
            individuals_dict[imported_individual.id] = individual
            if imported_individual.relationship == HEAD and household:
                household.head_of_household = individual

            (
                documents,
                identities,
            ) = self._prepare_individual_documents_and_identities(imported_individual, individual)

            documents_to_create.extend(documents)
            identities_to_create.extend(identities)

        return individuals_dict, documents_to_create, identities_to_create

    def _prepare_roles(
        self, imported_roles: List[IndividualRoleInHousehold], households_dict: Dict, individuals_dict: Dict
    ) -> List:
        roles_to_create = []
        for imported_role in imported_roles:
            role = IndividualRoleInHousehold(
                household=households_dict.get(imported_role.household.id),
                individual=individuals_dict.get(imported_role.individual.id),
                role=imported_role.role,
            )
            roles_to_create.append(role)

        return roles_to_create

    def _prepare_bank_account_info(
        self, imported_bank_account_infos: List[BankAccountInfo], individuals_dict: Dict
    ) -> List:
        roles_to_create = []
        for imported_bank_account_info in imported_bank_account_infos:
            role = BankAccountInfo(
                individual=individuals_dict.get(imported_bank_account_info.individual.id),
                bank_name=imported_bank_account_info.bank_name,
                bank_account_number=imported_bank_account_info.bank_account_number.replace(" ", ""),
                debit_card_number=imported_bank_account_info.debit_card_number.replace(" ", ""),
            )
            roles_to_create.append(role)

        return roles_to_create

    def execute(self, registration_data_import_id: str) -> None:
        individual_ids = []
        try:
            obj_hct = RegistrationDataImport.objects.get(id=registration_data_import_id)
            obj_hub = RegistrationDataImportDatahub.objects.get(hct_id=registration_data_import_id)
            imported_households = ImportedHousehold.objects.filter(registration_data_import=obj_hub)
            imported_individuals = ImportedIndividual.objects.filter(registration_data_import=obj_hub).order_by(
                "first_registration_date"
            )
            imported_roles = ImportedIndividualRoleInHousehold.objects.filter(
                household__in=imported_households, individual__in=imported_individuals
            )
            imported_bank_account_infos = ImportedBankAccountInfo.objects.filter(individual__in=imported_individuals)

            try:
                with transaction.atomic(using="default"), transaction.atomic(using="registration_datahub"):
                    old_obj_hct = copy_model_object(obj_hct)

                    households_dict = self._prepare_households(imported_households, obj_hct)
                    (
                        individuals_dict,
                        documents_to_create,
                        identities_to_create,
                    ) = self._prepare_individuals(imported_individuals, households_dict, obj_hct)

                    roles_to_create = self._prepare_roles(imported_roles, households_dict, individuals_dict)
                    bank_account_infos_to_create = self._prepare_bank_account_info(
                        imported_bank_account_infos, individuals_dict
                    )
                    logger.info(f"RDI:{registration_data_import_id} Creating {len(households_dict)} households")
                    Household.objects.bulk_create(households_dict.values())
                    Individual.objects.bulk_create(individuals_dict.values())
                    Document.objects.bulk_create(documents_to_create)
                    IndividualIdentity.objects.bulk_create(identities_to_create)
                    IndividualRoleInHousehold.objects.bulk_create(roles_to_create)
                    BankAccountInfo.objects.bulk_create(bank_account_infos_to_create)
                    logger.info(f"RDI:{registration_data_import_id} Created {len(households_dict)} households")
                    individual_ids = [str(individual.id) for individual in individuals_dict.values()]
                    household_ids = [str(household.id) for household in households_dict.values()]

                    transaction.on_commit(lambda: recalculate_population_fields_task(household_ids))
                    logger.info(
                        f"RDI:{registration_data_import_id} Recalculated population fields for {len(household_ids)} households"
                    )
                    kobo_submissions = []
                    for imported_household in imported_households:
                        kobo_submission_uuid = imported_household.kobo_submission_uuid
                        kobo_asset_id = imported_household.kobo_asset_id
                        kobo_submission_time = imported_household.kobo_submission_time
                        if kobo_submission_uuid and kobo_asset_id and kobo_submission_time:
                            submission = KoboImportedSubmission(
                                kobo_submission_uuid=kobo_submission_uuid,
                                kobo_asset_id=kobo_asset_id,
                                kobo_submission_time=kobo_submission_time,
                                registration_data_import=obj_hub,
                                imported_household=imported_household,
                            )
                            kobo_submissions.append(submission)
                    if kobo_submissions:
                        KoboImportedSubmission.objects.bulk_create(kobo_submissions)
                    logger.info(f"RDI:{registration_data_import_id} Created {len(kobo_submissions)} kobo submissions")

                    # DEDUPLICATION

                    populate_index(
                        Individual.objects.filter(registration_data_import=obj_hct),
                        get_individual_doc(obj_hct.business_area.slug),
                    )
                    logger.info(
                        f"RDI:{registration_data_import_id} Populated index for {len(individual_ids)} individuals"
                    )
                    populate_index(Household.objects.filter(registration_data_import=obj_hct), HouseholdDocument)
                    logger.info(
                        f"RDI:{registration_data_import_id} Populated index for {len(household_ids)} households"
                    )
                    if not obj_hct.business_area.postpone_deduplication:
                        individuals = evaluate_qs(
                            Individual.objects.filter(registration_data_import=obj_hct)
                            .select_for_update()
                            .order_by("pk")
                        )
                        DeduplicateTask(obj_hct.business_area.slug).deduplicate_individuals_against_population(
                            individuals
                        )
                        logger.info(f"RDI:{registration_data_import_id} Deduplicated {len(individual_ids)} individuals")
                        golden_record_duplicates = Individual.objects.filter(
                            registration_data_import=obj_hct, deduplication_golden_record_status=DUPLICATE
                        )
                        logger.info(
                            f"RDI:{registration_data_import_id} Found {len(golden_record_duplicates)} duplicates"
                        )

                        create_needs_adjudication_tickets(
                            golden_record_duplicates,
                            "duplicates",
                            obj_hct.business_area,
                            registration_data_import=obj_hct,
                        )
                        logger.info(
                            f"RDI:{registration_data_import_id} Created tickets for {len(golden_record_duplicates)} duplicates"
                        )

                        needs_adjudication = Individual.objects.filter(
                            registration_data_import=obj_hct, deduplication_golden_record_status=NEEDS_ADJUDICATION
                        )
                        logger.info(
                            f"RDI:{registration_data_import_id} Found {len(needs_adjudication)} needs adjudication"
                        )

                        create_needs_adjudication_tickets(
                            needs_adjudication,
                            "possible_duplicates",
                            obj_hct.business_area,
                            registration_data_import=obj_hct,
                        )
                        logger.info(
                            "RDI:{registration_data_import_id} Created tickets for {len(needs_adjudication)} needs adjudication"
                        )

                    # SANCTION LIST CHECK
                    if obj_hct.should_check_against_sanction_list():
                        logger.info(f"RDI:{registration_data_import_id} Checking against sanction list")
                        CheckAgainstSanctionListPreMergeTask.execute(registration_data_import=obj_hct)
                        logger.info(f"RDI:{registration_data_import_id} Checked against sanction list")

                    obj_hct.status = RegistrationDataImport.MERGED
                    obj_hct.save()
                    imported_households.delete()
                    logger.info(f"RDI:{registration_data_import_id} Saved registration data import")
                    transaction.on_commit(lambda: deduplicate_documents.delay())
                    log_create(RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", None, old_obj_hct, obj_hct)
                    logger.info(f"Datahub data for RDI: {obj_hct.id} was cleared")
            except Exception:
                # remove es individuals if exists
                remove_elasticsearch_documents_by_matching_ids(
                    individual_ids, get_individual_doc(obj_hct.business_area.slug)
                )

                # remove es households if exists
                remove_elasticsearch_documents_by_matching_ids(household_ids, HouseholdDocument)

                # proactively try to remove also es data for imported individuals
                remove_elasticsearch_documents_by_matching_ids(
                    list(imported_individuals.values_list("id", flat=True)),
                    get_imported_individual_doc(obj_hct.business_area.slug),
                )
                raise

            with contextlib.suppress(ConnectionError, AttributeError):
                for key in cache.keys("*"):
                    if key.startswith(
                        (
                            f"count_{obj_hub.business_area_slug}_HouseholdNodeConnection",
                            f"count_{obj_hub.business_area_slug}_IndividualNodeConnection",
                        )
                    ):
                        cache.delete(key)

        except Exception as e:
            logger.error(e)
            raise
