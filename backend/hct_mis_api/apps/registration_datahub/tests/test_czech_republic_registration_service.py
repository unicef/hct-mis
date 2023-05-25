import datetime

from django.test import TestCase
from django.utils import timezone

from django_countries.fields import Country

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.models import (
    FEMALE,
    GOVERNMENT_PARTNER,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    MALE,
    NOT_DISABLED,
    PRIVATE_PARTNER,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualRoleInHousehold,
    Record,
)
from hct_mis_api.apps.registration_datahub.services.czech_republic_flex_registration_service import (
    CzechRepublicFlexRegistration,
)


class TestCzechRepublicRegistrationService(TestCase):
    databases = {
        "default",
        "registration_datahub",
    }
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    @classmethod
    def setUp(cls) -> None:
        document_types_to_create = []

        for label in (
            IDENTIFICATION_TYPE_NATIONAL_ID,
            IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
            IDENTIFICATION_TYPE_DISABILITY_CERTIFICATE,
            IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
        ):
            document_types_to_create.append(
                ImportedDocumentType(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[label], label=label)
            )
        ImportedDocumentType.objects.bulk_create(document_types_to_create)

        BusinessArea.objects.create(
            **{
                "code": "BOCZ",
                "name": "Czech Republic",
                "region_name": "CZE",
                "slug": "czech-republic",
                "has_data_sharing_agreement": True,
            },
        )

        geo_models.Country.objects.create(name="Czechia")

        consent = [
            {
                "consent_h_c": "y",
                "consent_sharing_h_c": True,
                "government_partner": "",
                "consent_sharing_h_c_1": "y",
                "consent_sharing_h_c_2": "n",
            }
        ]

        needs_assessment = [
            {
                "access_education_rate_h_f": "Somewhat Easy",
                "access_health_rate_h_f": "A little Difficult",
                "access_leisure_activities_rate_h_f": "Very Easy",
                "access_social_services_rate_h_f": "Very Easy",
                "additional_support_h_f": "y",
                "adults_count_h_f": 2,
                "assistance_h_f": "y",
                "children_below_18_h_f": 3,
                "in_state_provided_accommodation_h_f": "no",
                "receiving_mop_h_f": "n",
                "school_enrolled_i_f": "no",
            }
        ]

        household_address = [
            {
                "address_h_c": "Opo\u010d\u00ednsk\u00e1 375",
                "admin1_h_c": "CZ010",
                "admin2_h_c": "CZ0109",
                "village_h_c": "Praha",
                "zip_code_h_c": "19017",
            }
        ]

        primary_carer_info = [
            {
                "bank_account_h_f": "y",
                "bank_account_number": "CZ6003000000000306979952",
                "bank_account_number_h_f": "CZ6003000000000306979952",
                "birth_date_i_c": "1995-08-01",
                "confirm_phone_number": "+420774844183",
                "country_origin_h_c": "ukr",
                "czech_formal_employment": "no",
                "family_name_i_c": "Symkanych",
                "gender_i_c": "female",
                "given_name_i_c": "Tetiana",
                "id_type_i_c": "national_passport",
                "national_passport_i_c": "GB500567",
                "other_communication_language": ["ru-ru"],
                "phone_no_i_c": "+420774844183",
                "preferred_language_i_c": "uk-ua",
                "primary_carer_is_legal_guardian": "y",
                "role_i_c": "primary",
                "work_status_i_c": "n",
            }
        ]

        children_information = [
            {
                "birth_certificate_no_i_c": "262873",
                "birth_date_i_c": "2013-07-04",
                "disability_i_c": "not disabled",
                "family_name_i_c": "Symkanych",
                "follow_up_needed": "n",
                "gender_i_c": "male",
                "given_name_i_c": "Ivan",
                "has_birth_certificate_i_c": "y",
                "other_id_no_i_c": "900541571",
                "preregistration_case_id": "13277",
                "qualifies_for_programme_i_f": "y",
                "relationship_i_c": "son_daughter",
            },
            {
                "gender_i_c": "female",
                "id_type_i_c": "national_id",
                "birth_date_i_c": "2023-04-30",
                "disability_i_c": "disabled",
                "follow_up_flag": ["legal_guardianship_documents"],
                "given_name_i_c": "TEST",
                "family_name_i_c": "TEST",
                "other_id_no_i_c": "TPV123",
                "follow_up_needed": "y",
                "relationship_i_c": "brother_sister",
                "follow_up_comments": "No comments",
                "national_id_no_i_c": "123214",
                "national_passport_i_c": "",
                "disability_card_i_c": "y",
                "disability_degree_i_c": "2",
                "disability_card_no_i_c": "1213",
                "medical_certificate_i_c": "y",
                "preregistration_case_id": "10937",
                "has_birth_certificate_i_c": "n",
                "medical_certificate_no_i_c": "2321",
                "qualifies_for_programme_i_f": "y",
                "disability_card_issuance_i_c": "2023-05-01",
                "proof_legal_guardianship_no_i_c": "128dj",
                "medical_certificate_issuance_i_c": "2023-05-01",
                "medical_certificate_validity_i_c": "2023-05-17",
                "has_disability_card_and_medical_cert": "Has Both",
            },
        ]

        legal_guardian_information = [
            {
                "gender_i_c": "male",
                "id_type_i_c": "national_passport",
                "phone_no_i_c": "+420123123666",
                "birth_date_i_c": "1988-12-27",
                "given_name_i_c": "Ivan",
                "family_name_i_c": "Drago",
                "relationship_i_c": "head",
                "confirm_phone_number": "+420123123666",
                "national_passport_i_c": "1234567890",
                "national_id_no_i_c": "",
                "legal_guardia_not_primary_carer": "y",
                "work_status_i_c": "y",
            }
        ]

        records = [
            Record(
                registration=25,
                timestamp=timezone.make_aware(datetime.datetime(2023, 5, 1)),
                source_id=1,
                fields={
                    "consent": consent,
                    "needs-assessment": needs_assessment,
                    "household-address": household_address,
                    "primary-carer-info": primary_carer_info,
                    "children-information": children_information,
                    "legal-guardian-information": legal_guardian_information,
                },
            )
        ]

        cls.records = Record.objects.bulk_create(records)
        cls.user = UserFactory.create()

    def test_import_data_to_datahub(self) -> None:
        service = CzechRepublicFlexRegistration()
        rdi = service.create_rdi(self.user, f"czech_republic rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids)

        self.records[0].refresh_from_db()
        self.assertEqual(
            Record.objects.filter(id__in=records_ids, ignored=False, status=Record.STATUS_IMPORTED).count(), 1
        )

        self.assertEqual(ImportedHousehold.objects.count(), 1)
        imported_household = ImportedHousehold.objects.first()
        self.assertEqual(imported_household.consent, True)
        self.assertEqual(imported_household.consent_sharing, [GOVERNMENT_PARTNER, PRIVATE_PARTNER])
        self.assertEqual(imported_household.country, Country(code="CZ"))
        self.assertEqual(imported_household.country_origin, Country(code="CZ"))
        self.assertEqual(imported_household.size, 4)
        self.assertEqual(imported_household.zip_code, "19017")
        self.assertEqual(imported_household.village, "Praha")
        self.assertEqual(imported_household.head_of_household, ImportedIndividual.objects.get(full_name="Ivan Drago"))

        self.assertEqual(ImportedIndividual.objects.count(), imported_household.size)
        head_of_household = ImportedIndividual.objects.get(full_name="Ivan Drago")
        self.assertEqual(head_of_household.sex, MALE)
        self.assertEqual(head_of_household.phone_no, "+420123123666")
        self.assertEqual(head_of_household.disability, NOT_DISABLED)
        self.assertEqual(head_of_household.work_status, "1")
        primary_collector = ImportedIndividual.objects.get(full_name="Tetiana Symkanych")
        self.assertEqual(primary_collector.sex, FEMALE)
        self.assertEqual(primary_collector.phone_no, "+420774844183")
        self.assertEqual(primary_collector.disability, NOT_DISABLED)
        self.assertEqual(primary_collector.work_status, "0")
        self.assertEqual(ImportedIndividualRoleInHousehold.objects.count(), 1)
        primary_role = ImportedIndividualRoleInHousehold.objects.first()
        self.assertEqual(primary_role.individual, primary_collector)
        self.assertEqual(primary_role.household, imported_household)

        self.assertEqual(ImportedBankAccountInfo.objects.count(), 1)
        bank_account_info = ImportedBankAccountInfo.objects.first()
        self.assertEqual(bank_account_info.bank_account_number, "CZ6003000000000306979952")

        self.assertEqual(ImportedDocument.objects.count(), 5)
        birth_certificate = ImportedDocument.objects.filter(type__key="birth_certificate").first()
        self.assertEqual(birth_certificate.document_number, "262873")
        self.assertEqual(ImportedDocument.objects.filter(type__key="disability_certificate").count(), 1)
        self.assertEqual(ImportedDocument.objects.filter(type__key="national_passport").count(), 2)
        national_passport = ImportedDocument.objects.filter(document_number="GB500567").first()
        self.assertEqual(national_passport.individual, primary_collector)
