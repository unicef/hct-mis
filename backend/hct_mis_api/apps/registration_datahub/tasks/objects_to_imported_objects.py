import logging
from typing import Dict, List, Tuple

from django.db import transaction
from django.forms import model_to_dict
from django.utils import timezone

from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.models import (
    HEAD,
    BankAccountInfo,
    Household,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualIdentity,
    ImportedIndividualRoleInHousehold,
    Record,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.utils.phone import is_valid_phone_number

logger = logging.getLogger(__name__)


class CreateImportedObjectsFromObjectsTask:
    """
    Reversed RdiMergeTask, creation of imported objects from objects, like ImportedHousehold from Household etc.
    """

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
        "detail_id",
        "collect_type",
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
        "detail_id",
        "disability_certificate_picture",
        "preferred_language",
        "age_at_registration",
    )

    def unmerge_admin_areas(
        self,
        household: Household,
        imported_household: ImportedHousehold,
    ) -> None:
        admins = {
            "admin_area": household.admin_area,
            "admin1": household.admin1,
            "admin2": household.admin2,
            "admin3": household.admin3,
            "admin4": household.admin4,
        }

        for admin_key, admin_value in admins.items():
            if admin_value:
                setattr(imported_household, admin_key, admin_value.p_code)

    def _prepare_imported_households(
        self,
        households: List[Household],
        obj_hct: RegistrationDataImportDatahub,
        import_to_program_id: str,
    ) -> Dict[int, ImportedHousehold]:
        imported_households_dict = {}
        countries = {}
        for household in households:
            household_data = {**model_to_dict(household, fields=self.HOUSEHOLD_FIELDS)}
            country = Country.objects.filter(id=household_data.pop("country")).first()
            country_origin = Country.objects.filter(id=household_data.pop("country_origin")).first()
            if country and country.iso_code2 not in countries:
                countries[country.iso_code2] = household.country.iso_code2
            if country_origin and country_origin.iso_code2 not in countries:
                countries[country_origin.iso_code2] = household.country_origin.iso_code2

            if country and (country := countries.get(country.iso_code2)):
                household_data["country"] = country

            if country_origin and (country_origin := countries.get(country_origin.iso_code2)):
                household_data["country_origin"] = country_origin

            if registration := household.registration_id:
                # new Record object, needed only to hold registration value
                household_data["flex_registrations_record"] = Record.objects.create(
                    registration=registration,
                    timestamp=timezone.now(),
                    source_id=0,
                )

            if enumerator_rec_id := household.flex_fields.get("enumerator_id"):
                household_data["enumerator_rec_id"] = enumerator_rec_id

            imported_household = ImportedHousehold(
                **household_data,
                registration_data_import=obj_hct,
                program_id=import_to_program_id,
                mis_unicef_id=household.unicef_id,
            )
            self.unmerge_admin_areas(household, imported_household)
            imported_households_dict[household.id] = imported_household

        return imported_households_dict

    def _prepare_imported_individual_documents_and_identities(
        self, individual: Individual, imported_individual: ImportedIndividual
    ) -> Tuple[List, List]:
        imported_documents_to_create = []
        for document in individual.documents.all():
            imported_document_type = ImportedDocumentType.objects.get(key=document.type.key)
            imported_document = ImportedDocument(
                document_number=document.document_number,
                country=document.country.iso_code2,
                type=imported_document_type,
                individual=imported_individual,
                photo=document.photo,
                expiry_date=document.expiry_date,
                issuance_date=document.issuance_date,
            )
            imported_documents_to_create.append(imported_document)
        imported_identities_to_create = []
        for identity in individual.identities.all():
            partner_name = identity.partner.name if identity.partner else None
            imported_identity = ImportedIndividualIdentity(
                partner=partner_name,
                document_number=identity.number,
                individual=imported_individual,
                country=identity.country.iso_code2,
            )
            imported_identities_to_create.append(imported_identity)

        return imported_documents_to_create, imported_identities_to_create

    def _prepare_imported_individuals(
        self,
        individuals: List[Individual],
        imported_households_dict: Dict[int, ImportedHousehold],
        import_to_program_id: str,
        obj_hub: RegistrationDataImportDatahub,
    ) -> Tuple[Dict, List, List]:
        imported_individuals_dict = {}
        imported_documents_to_create = []
        imported_identities_to_create = []
        for individual in individuals:
            values = model_to_dict(individual, fields=self.INDIVIDUAL_FIELDS)

            imported_household = imported_households_dict.get(individual.household.id) if individual.household else None

            phone_no = values.get("phone_no")
            phone_no_alternative = values.get("phone_no_alternative")

            values["phone_no_valid"] = is_valid_phone_number(str(phone_no))
            values["phone_no_alternative_valid"] = is_valid_phone_number(str(phone_no_alternative))

            imported_individual = ImportedIndividual(
                **values,
                household=imported_household,
                registration_data_import=obj_hub,
                program_id=import_to_program_id,
                mis_unicef_id=individual.unicef_id,
                payment_delivery_phone_no=individual.payment_delivery_phone_no or "",
            )

            if (
                imported_household
                and individual.household
                and getattr(individual, "heading_household", None) == individual.household
            ):
                imported_household.head_of_household = imported_individual
                # this relationship needs to be change for future steps -
                # it indicates that this individual is head of household (even tho head_of_household field is set on hh)
                imported_individual.relationship = HEAD

            imported_individuals_dict[individual.id] = imported_individual

            (
                imported_documents,
                imported_identities,
            ) = self._prepare_imported_individual_documents_and_identities(individual, imported_individual)

            imported_documents_to_create.extend(imported_documents)
            imported_identities_to_create.extend(imported_identities)

        return imported_individuals_dict, imported_documents_to_create, imported_identities_to_create

    def _prepare_imported_roles(
        self, roles: List[IndividualRoleInHousehold], households_dict: Dict, individuals_dict: Dict
    ) -> List:
        imported_roles_to_create = []
        for role in roles:
            imported_role = ImportedIndividualRoleInHousehold(
                household=households_dict.get(role.household.id),
                individual=individuals_dict.get(role.individual.id),
                role=role.role,
            )
            imported_roles_to_create.append(imported_role)

        return imported_roles_to_create

    def _prepare_imported_bank_account_info(
        self, bank_account_infos: List[BankAccountInfo], individuals_dict: Dict
    ) -> List:
        imported_bank_account_info_to_create = []
        for bank_account_info in bank_account_infos:
            imported_role = ImportedBankAccountInfo(
                individual=individuals_dict.get(bank_account_info.individual.id),
                bank_name=bank_account_info.bank_name,
                bank_account_number=bank_account_info.bank_account_number.replace(" ", ""),
                debit_card_number=bank_account_info.debit_card_number.replace(" ", ""),
                bank_branch_name=bank_account_info.bank_branch_name,
                account_holder_name=bank_account_info.account_holder_name,
            )
            imported_bank_account_info_to_create.append(imported_role)

        return imported_bank_account_info_to_create

    def execute(self, registration_data_import_id: str, import_from_program_id: str) -> None:
        try:
            obj_hct = RegistrationDataImport.objects.get(id=registration_data_import_id)
            obj_hub = RegistrationDataImportDatahub.objects.get(hct_id=registration_data_import_id)
            import_to_program_id = obj_hct.program.id
            households = Household.objects.filter(
                program=import_from_program_id,
                withdrawn=False,
            ).exclude(household_collection__households__program=import_to_program_id)
            individuals = (
                Individual.objects.filter(
                    program=import_from_program_id,
                    withdrawn=False,
                    duplicate=False,
                )
                .exclude(individual_collection__individuals__program=import_to_program_id)
                .order_by("first_registration_date")
            )
            roles = IndividualRoleInHousehold.objects.filter(household__in=households, individual__in=individuals)
            bank_account_infos = BankAccountInfo.objects.filter(individual__in=individuals)
            with transaction.atomic(using="default"), transaction.atomic(using="registration_datahub"):
                imported_households_dict = self._prepare_imported_households(households, obj_hub, import_to_program_id)
                (
                    imported_individuals_dict,
                    imported_documents_to_create,
                    imported_identities_to_create,
                ) = self._prepare_imported_individuals(
                    individuals,
                    imported_households_dict,
                    import_to_program_id,
                    obj_hub,
                )

                imported_roles_to_create = self._prepare_imported_roles(
                    roles,
                    imported_households_dict,
                    imported_individuals_dict,
                )
                imported_bank_account_infos_to_create = self._prepare_imported_bank_account_info(
                    bank_account_infos, imported_individuals_dict
                )
                logger.info(
                    f"RDI:{registration_data_import_id} "
                    f"Creating {len(imported_households_dict)} imported households"
                )
                ImportedHousehold.objects.bulk_create(imported_households_dict.values())
                ImportedIndividual.objects.bulk_create(imported_individuals_dict.values())
                ImportedDocument.objects.bulk_create(imported_documents_to_create)
                ImportedIndividualIdentity.objects.bulk_create(imported_identities_to_create)
                ImportedIndividualRoleInHousehold.objects.bulk_create(imported_roles_to_create)
                ImportedBankAccountInfo.objects.bulk_create(imported_bank_account_infos_to_create)
                logger.info(
                    f"RDI:{registration_data_import_id} " f"Created {len(imported_households_dict)} imported households"
                )
        except Exception as e:  # pragma: no cover
            logger.error(e)
            raise
