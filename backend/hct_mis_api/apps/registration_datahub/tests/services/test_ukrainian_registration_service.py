import datetime
import json

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import DocumentType, IDENTIFICATION_TYPE_TAX_ID
from hct_mis_api.apps.registration_datahub.models import Record, ImportedHousehold, ImportedDocumentType
from hct_mis_api.apps.registration_datahub.services.flex_registration_service import FlexRegistrationService


class TestUkrainianRegistrationService(TestCase):
    databases = (
        "default",
        "registration_datahub",
    )

    @classmethod
    def setUp(self):
        ImportedDocumentType.objects.create(
            type=IDENTIFICATION_TYPE_TAX_ID, label=IDENTIFICATION_TYPE_TAX_ID, country="UA"
        )
        BusinessArea.objects.create(
            **{
                "code": "0060",
                "name": "Ukraine",
                "long_name": "Ukraine",
                "region_code": "64",
                "region_name": "SAR",
                "slug": "ukraine",
                "has_data_sharing_agreement": True,
            },
        )
        household = [
            {
                "residence_status_h_c": "non_host",
                "where_are_you_now": "",
                "admin1_h_c": "UA07",
                "admin2_h_c": "UA0702",
                "admin3_h_c": "UA0702001",
                "size_h_c": 5,
            }
        ]
        individual_wit_bank_account_and_tax_and_disability = {
            "disability_certificate_picture": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
            "tax_id_no_i_c": "123123123",
            "bank_account_h_f": "y",
            "relationship_i_c": "head",
            "given_name_i_c": "Jan",
            "family_name_i_c": "Romaniak",
            "patronymic": "Roman",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
        }
        individual_wit_bank_account_and_tax = {
            "disability_certificate_picture": None,
            "tax_id_no_i_c": "123123123",
            "bank_account_h_f": "y",
            "relationship_i_c": "head",
            "given_name_i_c": "Wiktor",
            "family_name_i_c": "Lamiący",
            "patronymic": "Stefan",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
        }
        individual_with_no_tax = {
            "disability_certificate_picture": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
            "tax_id_no_i_c": "",
            "bank_account_h_f": "y",
            "relationship_i_c": "head",
            "given_name_i_c": "Michał",
            "family_name_i_c": "Brzęczący",
            "patronymic": "Janusz",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
        }
        individual_without_bank_account = {
            "disability_certificate_picture": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=",
            "tax_id_no_i_c": "123123123",
            "bank_account_h_f": "",
            "relationship_i_c": "head",
            "given_name_i_c": "Aleksiej",
            "family_name_i_c": "Prysznicow",
            "patronymic": "Paweł",
            "birth_date": "1991-11-18",
            "gender_i_c": "male",
            "phone_no_i_c": "0501706662",
        }
        defaults = {
            "registration": 1,
            "timestamp": datetime.datetime(2022, 4, 1),
        }

        records = [
            Record(
                **defaults,
                source_id=1,
                storage=json.dumps(
                    {"household": household, "individuals": [individual_wit_bank_account_and_tax_and_disability]}
                ).encode("utf-8"),
            ),
            Record(
                **defaults,
                source_id=2,
                storage=json.dumps(
                    {"household": household, "individuals": [individual_wit_bank_account_and_tax]}
                ).encode("utf-8"),
            ),
            Record(
                **defaults,
                source_id=3,
                storage=json.dumps({"household": household, "individuals": [individual_with_no_tax]}).encode("utf-8"),
            ),
            Record(
                **defaults,
                source_id=4,
                storage=json.dumps({"household": household, "individuals": [individual_without_bank_account]}).encode(
                    "utf-8"
                ),
            ),
        ]
        self.records = Record.objects.bulk_create(records)
        self.user = UserFactory.create()

    def test_import_data_to_datahub(self):
        service = FlexRegistrationService()
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")

        service.process_records(rdi.id, [x.id for x in self.records])
        self.records[2].refresh_from_db()
        self.assertEqual(Record.objects.filter(ignored=False).count(), 4)
        self.assertEqual(ImportedHousehold.objects.count(), 4)

    def test_import_data_to_datahub_retry(self):
        service = FlexRegistrationService()
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")

        service.process_records(rdi.id, [x.id for x in self.records])
        self.records[2].refresh_from_db()
        self.assertEqual(Record.objects.filter(ignored=False).count(), 4)
        self.assertEqual(ImportedHousehold.objects.count(), 4)
        service = FlexRegistrationService()
        rdi = service.create_rdi(self.user, f"ukraine rdi {datetime.datetime.now()}")

        service.process_records(rdi.id, [x.id for x in self.records[:2]])
        self.assertEqual(Record.objects.filter(ignored=False).count(), 4)
        self.assertEqual(ImportedHousehold.objects.count(), 4)