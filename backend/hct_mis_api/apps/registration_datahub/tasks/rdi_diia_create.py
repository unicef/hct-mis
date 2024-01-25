import logging
from typing import TYPE_CHECKING, Dict, List, Optional

from django.core.exceptions import ValidationError
from django.db import transaction

import dateutil.parser
from django_countries.fields import Country

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.models import (
    DISABLED,
    FEMALE,
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_OTHER,
    IDENTIFICATION_TYPE_TAX_ID,
    MALE,
    NOT_DISABLED,
    RELATIONSHIP_UNKNOWN,
    SON_DAUGHTER,
    WIFE_HUSBAND,
    YES,
    Document,
    DocumentType,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    DIIA_DISABLED,
    DIIA_RELATIONSHIP_DAUGHTER,
    DIIA_RELATIONSHIP_HEAD,
    DIIA_RELATIONSHIP_HUSBAND,
    DIIA_RELATIONSHIP_SON,
    DIIA_RELATIONSHIP_WIFE,
    DiiaHousehold,
    DiiaIndividual,
    ImportData,
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask
from hct_mis_api.apps.utils.age_at_registration import calculate_age_at_registration

if TYPE_CHECKING:
    from uuid import UUID

    from hct_mis_api.apps.program.models import Program


logger = logging.getLogger(__name__)


class RdiDiiaCreateTask:
    """
    Imports project data from DIIA models
    """

    DIIA_DISABILITY_MAP = {DIIA_DISABLED: DISABLED}
    DIIA_RELATION = {
        DIIA_RELATIONSHIP_HEAD: HEAD,
        DIIA_RELATIONSHIP_SON: SON_DAUGHTER,
        DIIA_RELATIONSHIP_DAUGHTER: SON_DAUGHTER,
        DIIA_RELATIONSHIP_WIFE: WIFE_HUSBAND,
        DIIA_RELATIONSHIP_HUSBAND: WIFE_HUSBAND,
    }
    DIIA_SEX_MAP = {"M": MALE, "F": FEMALE}

    def __init__(self) -> None:
        self.bank_accounts = []
        self.documents = []
        self.business_area = BusinessArea.objects.get(slug="ukraine")

    @transaction.atomic("default")
    @transaction.atomic("registration_datahub")
    def create_rdi(
        self,
        imported_by: Optional[ImportedIndividual],
        program: "Program",
        rdi_name: str = "rdi_name",
        is_open: bool = False,
    ) -> RegistrationDataImport:
        number_of_individuals = 0
        number_of_households = 0
        status = RegistrationDataImport.LOADING if is_open else RegistrationDataImport.IMPORTING
        rdi = RegistrationDataImport.objects.create(
            name=rdi_name,
            data_source=RegistrationDataImport.DIIA,
            imported_by=imported_by,
            number_of_individuals=number_of_individuals,
            number_of_households=number_of_households,
            business_area=self.business_area,
            status=status,
            program=program,
        )

        import_data = ImportData.objects.create(
            status=ImportData.STATUS_PENDING,
            business_area_slug=self.business_area.slug,
            data_type=ImportData.DIIA,
            number_of_individuals=number_of_individuals,
            number_of_households=number_of_households,
            created_by_id=imported_by.id if imported_by else None,
        )
        rdi_datahub = RegistrationDataImportDatahub.objects.create(
            name=rdi_name,
            hct_id=rdi.id,
            import_data=import_data,
            import_done=RegistrationDataImportDatahub.NOT_STARTED,
            business_area_slug=self.business_area.slug,
        )
        rdi.datahub_id = rdi_datahub.id
        rdi.save()
        return rdi

    @transaction.atomic(using="default")
    @transaction.atomic(using="registration_datahub")
    def execute(
        self,
        registration_data_import_id: "UUID",
        diia_hh_ids: Optional[List["UUID"]] = None,
        diia_hh_count: Optional[int] = None,
    ) -> None:
        if diia_hh_ids and diia_hh_count:
            raise ValueError("You can't set two args diia_hh_ids and diia_hh_count")

        if not diia_hh_ids:
            diia_household_import_ids = DiiaHousehold.objects.filter(status=DiiaHousehold.STATUS_TO_IMPORT).values_list(
                "id", flat=True
            )[:diia_hh_count]
        else:
            diia_household_import_ids = DiiaHousehold.objects.filter(
                status=DiiaHousehold.STATUS_TO_IMPORT, id__in=diia_hh_ids
            ).values_list("id", flat=True)

        rdi_mis = RegistrationDataImport.objects.get(id=registration_data_import_id)
        program = rdi_mis.program

        registration_data_import_data_hub = RegistrationDataImportDatahub.objects.select_for_update().get(
            id=rdi_mis.datahub_id,
        )

        if not diia_household_import_ids:
            rdi_mis.delete()
            registration_data_import_data_hub.import_data.delete()
            registration_data_import_data_hub.delete()
            raise ValidationError("Rdi doesn't found any records within status to import")

        registration_data_import_data_hub.import_done = RegistrationDataImportDatahub.STARTED
        registration_data_import_data_hub.save()

        self._get_document_types()

        households_to_create = []
        households_to_update = []
        individual_count = 0

        for diia_household_id in diia_household_import_ids:
            diia_household = DiiaHousehold.objects.defer("source_data").get(id=diia_household_id)
            try:
                all_individuals = DiiaIndividual.objects.filter(rec_id=diia_household.rec_id)
                household_obj = ImportedHousehold(
                    consent=diia_household.consent,
                    address=diia_household.address,
                    registration_data_import=registration_data_import_data_hub,
                    first_registration_date=registration_data_import_data_hub.created_at,
                    last_registration_date=registration_data_import_data_hub.created_at,
                    collect_individual_data=YES,
                    diia_rec_id=diia_household.rec_id,
                    size=all_individuals.count(),
                    country=Country("UA"),
                    program_id=program.id,
                )

                # if True ignore create HH and Individuals and set status 'STATUS_TAX_ID_ERROR'
                pass_hh_and_individuals_tax_id_error = False

                individuals_to_create_list = []
                individuals_to_update_list = []
                head_of_household: ImportedIndividual
                self.bank_accounts = []
                self.documents = []
                individual_count += all_individuals.count()

                for individual in all_individuals:
                    if pass_hh_and_individuals_tax_id_error:
                        continue

                    # validate tax_id
                    if individual.individual_id and self.tax_id_exists(individual.individual_id.replace(" ", "")):
                        pass_hh_and_individuals_tax_id_error = True
                        individuals_to_create_list = []
                        individuals_to_update_list = []
                        individual_count -= all_individuals.count()
                        self.bank_accounts = []
                        self.documents = []
                        continue

                    b_date = (
                        dateutil.parser.parse(individual.birth_date, dayfirst=True) if individual.birth_date else ""
                    )

                    individual_obj = ImportedIndividual(
                        individual_id=individual.individual_id.replace(" ", "") if individual.individual_id else "",
                        given_name=individual.first_name,
                        middle_name=individual.second_name,
                        family_name=individual.last_name,
                        full_name=f"{individual.first_name} {individual.last_name}",
                        relationship=self.DIIA_RELATION.get(individual.relationship, RELATIONSHIP_UNKNOWN),
                        sex=self.DIIA_SEX_MAP.get(individual.sex, ""),
                        birth_date=b_date,
                        marital_status=individual.marital_status if individual.marital_status else "",
                        disability=self.DIIA_DISABILITY_MAP.get(individual.disability, NOT_DISABLED),
                        registration_data_import=registration_data_import_data_hub,
                        first_registration_date=registration_data_import_data_hub.created_at,
                        last_registration_date=registration_data_import_data_hub.created_at,
                        household=household_obj,
                        email=individual.email,
                        program_id=program.id,
                        age_at_registration=calculate_age_at_registration(
                            registration_data_import_data_hub, individual.birth_date
                        ),
                    )
                    individuals_to_create_list.append(individual_obj)

                    if individual.relationship == HEAD:
                        head_of_household = individual_obj

                        hh_doc = {
                            "type": individual.doc_type,
                            "document_number": f"{individual.doc_serie} {individual.doc_number}",
                            "doc_date": dateutil.parser.parse(individual.doc_issue_date, dayfirst=True)
                            if individual.doc_issue_date
                            else None,
                            "individual": individual_obj,
                        }
                        self._add_hh_doc(hh_doc)

                    if individual.birth_doc:
                        self._add_birth_document(individual, individual_obj)

                    if individual.iban:
                        self._add_bank_account(individual, individual_obj)

                    if individual.individual_id:
                        self._add_tax_id_document(individual.individual_id.replace(" ", ""), individual_obj)

                    individual.imported_individual = individual_obj
                    individuals_to_update_list.append(individual)

                # create Individuals
                ImportedIndividual.objects.bulk_create(individuals_to_create_list)
                # update imported_individual
                DiiaIndividual.objects.bulk_update(individuals_to_update_list, ["imported_individual"], 1000)

                if diia_household.vpo_doc and not pass_hh_and_individuals_tax_id_error:
                    self._add_vpo_document(head_of_household, diia_household)

                if not pass_hh_and_individuals_tax_id_error:
                    ImportedDocument.objects.bulk_create(self.documents)
                    ImportedBankAccountInfo.objects.bulk_create(self.bank_accounts)

                    household_obj.head_of_household = head_of_household
                    households_to_create.append(household_obj)
                    diia_household.imported_household = household_obj
                    diia_household.registration_data_import = registration_data_import_data_hub
                    diia_household.status = DiiaHousehold.STATUS_IMPORTED
                    households_to_update.append(diia_household)
                else:
                    # STATUS_TAX_ID_ERROR
                    logger.error(f"Error importing DiiaHousehold {diia_household.pk}, duplicate Tax ID.")
                    diia_household.status = DiiaHousehold.STATUS_TAX_ID_ERROR
                    households_to_update.append(diia_household)

            except Exception as e:
                logger.exception(f"Error importing DiiaHousehold {diia_household.pk}. {e}")
                diia_household.status = DiiaHousehold.STATUS_ERROR
                households_to_update.append(diia_household)

        ImportedHousehold.objects.bulk_create(households_to_create)
        DiiaHousehold.objects.bulk_update(
            households_to_update, ["imported_household", "status", "registration_data_import"], 1000
        )

        registration_data_import_data_hub.import_done = RegistrationDataImportDatahub.DONE
        registration_data_import_data_hub.save()

        registration_data_import_data_hub.import_data.number_of_individuals = individual_count
        registration_data_import_data_hub.import_data.number_of_households = len(households_to_create)
        registration_data_import_data_hub.import_data.status = ImportData.STATUS_FINISHED
        registration_data_import_data_hub.import_data.save()

        rdi_mis.status = RegistrationDataImport.IN_REVIEW
        rdi_mis.number_of_individuals = individual_count
        rdi_mis.number_of_households = len(households_to_create)
        rdi_mis.save()
        log_create(
            RegistrationDataImport.ACTIVITY_LOG_MAPPING, "business_area", None, rdi_mis.program_id, rdi_mis, rdi_mis
        )
        if not rdi_mis.business_area.postpone_deduplication:
            DeduplicateTask(
                business_area_slug=registration_data_import_data_hub.business_area_slug, program_id=program.id
            ).deduplicate_imported_individuals(registration_data_import_datahub=registration_data_import_data_hub)

    def _add_bank_account(self, individual: ImportedIndividual, individual_obj: ImportedIndividual) -> None:
        self.bank_accounts.append(
            ImportedBankAccountInfo(
                individual=individual_obj,
                bank_name=individual.bank_name,
                bank_account_number=individual.iban.replace(" ", ""),
            )
        )

    def _add_vpo_document(self, head_of_household: ImportedIndividual, household: ImportedHousehold) -> None:
        vpo_doc_date = dateutil.parser.parse(household.vpo_doc_date)

        self.documents.append(
            ImportedDocument(
                country=Country("UA"),
                document_number=household.vpo_doc_id,
                individual=head_of_household,
                type=self.other_document_type,
                photo=household.vpo_doc,
                doc_date=vpo_doc_date,
            )
        )

    def _add_birth_document(self, individual: ImportedIndividual, individual_obj: ImportedIndividual) -> None:
        self.documents.append(
            ImportedDocument(
                country=Country("UA"),
                document_number=individual.birth_doc,
                individual=individual_obj,
                type=self.birth_document_type,
            )
        )

    def _add_hh_doc(self, data: Dict) -> None:
        doc_type = self.national_passport_document_type if data.get("type") == "passport" else self.other_document_type

        self.documents.append(
            ImportedDocument(
                country=Country("UA"),
                document_number=data.get("document_number"),
                individual=data.get("individual"),
                doc_date=data.get("doc_date"),
                type=doc_type,
            )
        )

    def _add_tax_id_document(self, tax_id: "UUID", individual_obj: ImportedIndividual) -> None:
        self.documents.append(
            ImportedDocument(
                country=Country("UA"),
                document_number=tax_id,
                individual=individual_obj,
                type=self.imported_doc_type_for_tax_id,
            )
        )

    def _get_document_types(self) -> None:
        self.national_passport_document_type = ImportedDocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_PASSPORT],
        )
        self.birth_document_type = ImportedDocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
        )
        self.other_document_type = ImportedDocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_OTHER],
        )
        self.imported_doc_type_for_tax_id = ImportedDocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
        )
        self.doc_type_for_tax_id = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
        )

    def tax_id_exists(self, tax_id: "UUID") -> bool:
        return (
            ImportedDocument.objects.filter(document_number=tax_id, type=self.imported_doc_type_for_tax_id).exists()
            or Document.objects.filter(document_number=tax_id, type=self.doc_type_for_tax_id).exists()
        )