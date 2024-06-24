import json
import secrets
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any, Dict
from unittest import mock

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.files import File
from django.db.models.fields.files import ImageFieldFile
from django.forms import model_to_dict

from django_countries.fields import Country
from PIL import Image

from hct_mis_api.apps.account.fixtures import PartnerFactory
from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import (
    IDENTIFICATION_TYPE_TO_KEY_MAPPING,
    SheetImageLoader,
)
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.models import Country as GeoCountry
from hct_mis_api.apps.household.fixtures import IndividualFactory
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_CHOICE,
    IDENTIFICATION_TYPE_TAX_ID,
    BankAccountInfo,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
)
from hct_mis_api.apps.payment.models import PendingDeliveryMechanismData
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import ImportData, RegistrationDataImport
from hct_mis_api.apps.registration_datahub.fixtures import (
    ImportedIndividualFactory,
    RegistrationDataImportDatahubFactory,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
)
from hct_mis_api.apps.utils.models import MergeStatusModel


def create_document_image() -> File:
    content = Path(f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/image.png").read_bytes()
    return File(BytesIO(content), name="image.png")


class ImageLoaderMock(SheetImageLoader):
    def __init__(self) -> None:
        pass

    def image_in(self, *args: Any, **kwargs: Any) -> bool:
        return True

    def get(self, *args: Any, **kwargs: Any) -> Image:
        return Image.open(create_document_image())


class CellMock:
    def __init__(self, value: Any, coordinate: Any) -> None:
        self.value = value
        self.coordinate = coordinate


class TestRdiCreateTask(BaseElasticSearchTestCase):
    databases = {
        "default",
        "registration_datahub",
    }
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/new_reg_data_import.xlsx"
        ).read_bytes()
        file = File(BytesIO(content), name="new_reg_data_import.xlsx")
        business_area = create_afghanistan()

        from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create import (
            RdiXlsxCreateTask,
        )

        PartnerFactory(name="WFP")
        PartnerFactory(name="UNHCR")

        cls.RdiXlsxCreateTask = RdiXlsxCreateTask

        cls.import_data = ImportData.objects.create(
            file=file,
            number_of_households=3,
            number_of_individuals=6,
        )

        cls.program = ProgramFactory(status=Program.ACTIVE)

        cls.registration_data_import = RegistrationDataImportDatahubFactory(
            import_data=cls.import_data, business_area_slug=business_area.slug, hct_id=None
        )
        hct_rdi = RegistrationDataImportFactory(
            datahub_id=cls.registration_data_import.id,
            name=cls.registration_data_import.name,
            business_area=business_area,
            program=cls.program,
        )
        cls.registration_data_import.hct_id = hct_rdi.id
        cls.registration_data_import.save()
        cls.business_area = BusinessArea.objects.first()
        DocumentType.objects.create(
            label="Tax Number Identification",
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
        )
        super().setUpTestData()

    def test_execute(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        households_count = Household.objects.count()
        individuals_count = Individual.objects.count()

        self.assertEqual(3, households_count)
        self.assertEqual(6, individuals_count)

        individual_data = {
            "full_name": "Some Full Name",
            "given_name": "Some",
            "middle_name": "Full",
            "family_name": "Name",
            "sex": "MALE",
            "relationship": "HEAD",
            "birth_date": date(1963, 2, 3),
            "marital_status": "MARRIED",
            "email": "fake_email_123@mail.com",
        }
        matching_individuals = Individual.objects.filter(**individual_data)

        self.assertEqual(matching_individuals.count(), 1)

        household_data = {
            "residence_status": "REFUGEE",
            "country": GeoCountry.objects.get(iso_code2="AF").id,
            "zip_code": "2153",
            "flex_fields": {"enumerator_id": "UNICEF"},
        }
        household = matching_individuals.first().household
        household_obj_data = model_to_dict(household, ("residence_status", "country", "zip_code", "flex_fields"))

        roles = household.individuals_and_roles.all()
        self.assertEqual(roles.count(), 1)
        role = roles.first()
        self.assertEqual(role.role, "PRIMARY")
        self.assertEqual(role.individual.full_name, "Some Full Name")

        self.assertEqual(household_obj_data, household_data)

    def test_execute_handle_identities(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
            self.program.id,
        )
        self.assertEqual(IndividualIdentity.objects.count(), 2)
        self.assertEqual(
            IndividualIdentity.objects.filter(
                number="TEST", country__iso_code2="PL", partner__name="WFP", individual__full_name="Some Full Name"
            ).count(),
            1,
        )
        self.assertEqual(
            IndividualIdentity.objects.filter(
                number="WTG", country__iso_code2="PL", partner__name="UNHCR", individual__full_name="Some Full Name"
            ).count(),
            1,
        )

    def test_handle_document_fields(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.documents = {}
        individual = ImportedIndividualFactory()

        header = "birth_certificate_no_i_c"
        row_num = 14

        # when value is empty
        value = None
        task._handle_document_fields(
            value,
            header,
            row_num,
            individual,
        )
        self.assertEqual(task.documents, {})

        # when value is valid for header of not other type
        value = "AB1247246Q12W"
        task._handle_document_fields(
            value,
            header,
            row_num,
            individual,
        )
        expected = {
            "individual_14_birth_certificate_i_c": {
                "individual": individual,
                "key": "birth_certificate",
                "value": value,
            }
        }

        self.assertEqual(task.documents, expected)

        number = "CD1247246Q12W"
        header = "other_id_no_i_c"
        task._handle_document_fields(
            number,
            header,
            row_num,
            individual,
        )
        expected = {
            "individual_14_birth_certificate_i_c": {
                "individual": individual,
                "key": "birth_certificate",
                "value": value,
            },
            "individual_14_other_id_i_c": {"individual": individual, "key": "other_id", "value": number},
        }
        self.assertEqual(task.documents, expected)

    @mock.patch(
        "hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create.SheetImageLoader",
        ImageLoaderMock,
    )
    @mock.patch(
        "hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_create.timezone.now",
        lambda: "2020-06-22 12:00:00-0000",
    )
    def test_handle_document_photo_fields(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.image_loader = ImageLoaderMock()
        task.documents = {}
        individual = ImportedIndividualFactory()
        cell = CellMock("image.png", 12)

        task._handle_document_photo_fields(
            cell,
            14,
            individual,
            "birth_certificate_photo_i_c",
        )
        self.assertIn("individual_14_birth_certificate_i_c", task.documents.keys())
        birth_certificate = task.documents["individual_14_birth_certificate_i_c"]
        self.assertEqual(birth_certificate["individual"], individual)
        self.assertEqual(birth_certificate["photo"].name, "12-2020-06-22 12:00:00-0000.jpg")

        birth_cert_doc = {
            "individual_14_birth_certificate_i_c": {
                "individual": individual,
                "name": "Birth Certificate",
                "type": "BIRTH_CERTIFICATE",
                "value": "CD1247246Q12W",
            }
        }
        task.documents = birth_cert_doc
        task._handle_document_photo_fields(
            cell,
            14,
            individual,
            "birth_certificate_photo_i_c",
        )

        self.assertIn("individual_14_birth_certificate_i_c", task.documents.keys())
        birth_certificate = task.documents["individual_14_birth_certificate_i_c"]
        self.assertEqual(birth_certificate["name"], "Birth Certificate")
        self.assertEqual(birth_certificate["type"], "BIRTH_CERTIFICATE")
        self.assertEqual(birth_certificate["value"], "CD1247246Q12W")
        self.assertEqual(birth_certificate["photo"].name, "12-2020-06-22 12:00:00-0000.jpg")

    def test_handle_geopoint_field(self) -> None:
        empty_geopoint = ""
        valid_geopoint = "51.107883, 17.038538"
        task = self.RdiXlsxCreateTask()

        result = task._handle_geopoint_field(empty_geopoint)
        self.assertEqual(result, "")

        expected = Point(x=51.107883, y=17.038538, srid=4326)
        result = task._handle_geopoint_field(valid_geopoint)
        self.assertEqual(result, expected)

    def test_create_documents(self) -> None:
        task = self.RdiXlsxCreateTask()
        individual = IndividualFactory()
        task.business_area = self.business_area
        doc_type = DocumentType.objects.create(
            label="Birth Certificate",
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
        )
        task.documents = {
            "individual_14_birth_certificate_i_c": {
                "individual": individual,
                "name": "Birth Certificate",
                "key": "birth_certificate",
                "value": "CD1247246Q12W",
                "issuing_country": Country("AFG"),
                "photo": create_document_image(),
            }
        }
        task._create_documents()

        documents = Document.objects.values("document_number", "type_id")
        self.assertEqual(documents.count(), 1)

        expected = [{"document_number": "CD1247246Q12W", "type_id": doc_type.id}]
        self.assertEqual(list(documents), expected)

        document = Document.objects.first()
        photo = document.photo.name
        self.assertTrue(photo.startswith("image"))
        self.assertTrue(photo.endswith(".png"))

    def test_cast_value(self) -> None:
        task = self.RdiXlsxCreateTask()

        # None and ""
        result = task._cast_value(None, "test_header")
        self.assertIsNone(result)

        result = task._cast_value("", "test_header")
        self.assertEqual(result, "")

        # INTEGER - header: size_h_c
        result = task._cast_value("12", "size_h_c")
        self.assertEqual(result, 12)

        result = task._cast_value(12.0, "size_h_c")
        self.assertEqual(result, 12)

        # SELECT_ONE - header: gender_i_c
        result = task._cast_value("male", "gender_i_c")
        self.assertEqual(result, "MALE")

        result = task._cast_value("Male", "gender_i_c")
        self.assertEqual(result, "MALE")

        result = task._cast_value("MALE", "gender_i_c")
        self.assertEqual(result, "MALE")

        result = task._cast_value("TRUE", "estimated_birth_date_i_c")
        self.assertEqual(result, True)

        result = task._cast_value("true", "estimated_birth_date_i_c")
        self.assertEqual(result, True)

        result = task._cast_value("True", "estimated_birth_date_i_c")
        self.assertEqual(result, True)

    def test_store_row_id(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        households = ImportedHousehold.objects.all()
        for household in households:
            self.assertTrue(int(household.detail_id) in [3, 4, 6])

        individuals = ImportedIndividual.objects.all()
        for individual in individuals:
            self.assertTrue(int(individual.detail_id) in [3, 4, 5, 7, 8, 9])

    def test_create_bank_account(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        bank_account_info = BankAccountInfo.objects.get(individual__detail_id=7)
        self.assertEqual(bank_account_info.bank_name, "Bank testowy")
        self.assertEqual(bank_account_info.bank_account_number, "PL70 1410 2006 0000 3200 0926 4671")
        self.assertEqual(bank_account_info.debit_card_number, "5241 6701 2345 6789")

    def test_create_tax_id_document(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        document = Document.objects.filter(individual__detail_id=5).first()
        self.assertEqual(document.type.key, IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID])
        self.assertEqual(document.document_number, "CD1247246Q12W")

    def test_import_empty_cell_as_blank_cell(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        individual = Individual.objects.get(detail_id=3)
        self.assertEqual(individual.seeing_disability, "")
        self.assertEqual(individual.hearing_disability, "")

    def test_create_receiver_poi_document(self) -> None:
        task = self.RdiXlsxCreateTask()
        individual = IndividualFactory()
        task.business_area = self.business_area
        doc_type = DocumentType.objects.get_or_create(
            label="Receiver POI",
            key="receiver_poi",
        )[0]
        task.documents = {
            "individual_10_receiver_poi_i_c": {
                "individual": individual,
                "name": "Receiver POI",
                "key": "receiver_poi",
                "value": "TEST123_qwerty",
                "issuing_country": Country("AFG"),
                "photo": None,
            }
        }
        task._create_documents()

        documents = Document.objects.values("document_number", "type_id")
        self.assertEqual(documents.count(), 1)

        expected = [{"document_number": "TEST123_qwerty", "type_id": doc_type.id}]
        self.assertEqual(list(documents), expected)

    def test_create_delivery_mechanism_data(self) -> None:
        task = self.RdiXlsxCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)
        self.assertEqual(PendingDeliveryMechanismData.objects.count(), 3)

        dmd1 = PendingDeliveryMechanismData.objects.get(individual__detail_id=3)
        dmd2 = PendingDeliveryMechanismData.objects.get(individual__detail_id=4)
        dmd3 = PendingDeliveryMechanismData.objects.get(individual__detail_id=5)
        self.assertEqual(dmd1.rdi_merge_status, MergeStatusModel.PENDING)
        self.assertEqual(dmd2.rdi_merge_status, MergeStatusModel.PENDING)
        self.assertEqual(dmd3.rdi_merge_status, MergeStatusModel.PENDING)
        self.assertEqual(
            json.loads(dmd1.data),
            {"card_number_atm_card": "164260858", "card_expiry_date_atm_card": "1995-06-03T00:00:00"},
        )
        self.assertEqual(
            json.loads(dmd2.data),
            {
                "card_number_atm_card": "1975549730",
                "card_expiry_date_atm_card": "2022-02-17T00:00:00",
                "name_of_cardholder_atm_card": "Name1",
            },
        )
        self.assertEqual(
            json.loads(dmd3.data),
            {
                "card_number_atm_card": "870567340",
                "card_expiry_date_atm_card": "2016-06-27T00:00:00",
                "name_of_cardholder_atm_card": "Name2",
            },
        )


class TestRdiKoboCreateTask(BaseElasticSearchTestCase):
    databases = {
        "default",
        "registration_datahub",
    }
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @staticmethod
    def _return_test_image(*args: Any, **kwargs: Any) -> BytesIO:
        return BytesIO(
            Path(f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/image.png").read_bytes()
        )

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        from hct_mis_api.apps.registration_datahub.tasks.rdi_kobo_create import (
            RdiKoboCreateTask,
        )

        cls.RdiKoboCreateTask = RdiKoboCreateTask

        identification_type_choice = tuple((doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE)
        document_types = []
        for doc_type, label in identification_type_choice:
            document_types.append(ImportedDocumentType(label=label, key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[doc_type]))
        ImportedDocumentType.objects.bulk_create(document_types, ignore_conflicts=True)

        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/kobo_submissions.json"
        ).read_bytes()
        file = File(BytesIO(content), name="kobo_submissions.json")
        cls.import_data = ImportData.objects.create(
            file=file,
            number_of_households=1,
            number_of_individuals=2,
        )

        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/kobo_submissions_collectors.json"
        ).read_bytes()
        file = File(BytesIO(content), name="kobo_submissions_collectors.json")
        cls.import_data_collectors = ImportData.objects.create(
            file=file,
            number_of_households=2,
            number_of_individuals=5,
        )

        cls.business_area = BusinessArea.objects.first()
        cls.business_area.kobo_username = "1234ABC"
        cls.business_area.save()

        country = geo_models.Country.objects.first()

        admin1_type = geo_models.AreaType.objects.create(name="Bakool", area_level=1, country=country)
        admin1 = geo_models.Area.objects.create(p_code="SO25", name="SO25", area_type=admin1_type)

        admin2_type = geo_models.AreaType.objects.create(name="Ceel Barde", area_level=2, country=country)
        geo_models.Area.objects.create(p_code="SO2502", name="SO2502", parent=admin1, area_type=admin2_type)

        cls.registration_data_import = RegistrationDataImportDatahubFactory(
            import_data=cls.import_data, business_area_slug=cls.business_area.slug
        )
        cls.program = ProgramFactory(status="ACTIVE")
        hct_rdi = RegistrationDataImportFactory(
            datahub_id=cls.registration_data_import.id,
            name=cls.registration_data_import.name,
            business_area=cls.business_area,
            program=cls.program,
        )
        cls.registration_data_import.hct_id = hct_rdi.id
        cls.registration_data_import.save()
        super().setUpTestData()

    @mock.patch(
        "hct_mis_api.apps.registration_datahub.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_execute(self) -> None:
        task = self.RdiKoboCreateTask()
        task.execute(self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id)

        households = ImportedHousehold.objects.all()
        individuals = ImportedIndividual.objects.all()
        documents = ImportedDocument.objects.all()
        bank_accounts = ImportedBankAccountInfo.objects.all()

        self.assertEqual(1, households.count())
        self.assertEqual(2, individuals.count())
        self.assertEqual(3, documents.count())
        self.assertEqual(1, bank_accounts.count())

        individual = individuals.get(full_name="Test Testowski")

        individuals_obj_data = model_to_dict(
            individual,
            ("country", "sex", "age", "marital_status", "relationship"),
        )
        expected_ind: Dict = {
            "relationship": "HEAD",
            "sex": "MALE",
            "marital_status": "MARRIED",
        }
        self.assertEqual(individuals_obj_data, expected_ind)

        household_obj_data = model_to_dict(individual.household, ("residence_status", "country", "flex_fields"))
        expected_hh: Dict = {
            "residence_status": "REFUGEE",
            "country": Country(code="AF"),
            "flex_fields": {},
        }
        self.assertEqual(household_obj_data, expected_hh)

        self.assertEqual(individual.household.detail_id, "aPkhoRMrkkDwgsvWuwi39s")
        self.assertEqual(str(individual.household.kobo_submission_uuid), "c09130af-6c9c-4dba-8c7f-1b2ff1970d19")
        self.assertEqual(individual.household.kobo_submission_time.isoformat(), "2020-06-03T13:05:10+00:00")

    @mock.patch(
        "hct_mis_api.apps.registration_datahub.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_execute_multiple_collectors(self) -> None:
        task = self.RdiKoboCreateTask()
        task.execute(
            self.registration_data_import.id, self.import_data_collectors.id, self.business_area.id, self.program.id
        )
        households = ImportedHousehold.objects.all()
        individuals = ImportedIndividual.objects.all()

        self.assertEqual(households.count(), 3)  # related to AB#171697
        self.assertEqual(individuals.count(), 7)  # related to AB#171697

        documents = ImportedDocument.objects.values_list("individual__full_name", flat=True)
        self.assertEqual(
            sorted(list(documents)),
            [
                "Tesa Testowski 222",
                "Tesa XLast",
                "Test Testowski 222",
                "XLast XFull XName",
                "Zbyszek Zbyszkowski",
                "abc efg",
            ],
        )

        first_household = households.get(size=3, individuals__full_name="Tesa Testowski 222")
        second_household = households.get(
            size=2,
        )

        first_household_collectors = first_household.individuals_and_roles.order_by(
            "individual__full_name"
        ).values_list("individual__full_name", "role")
        self.assertEqual(
            list(first_household_collectors),
            [("Tesa Testowski 222", "ALTERNATE"), ("Test Testowski 222", "PRIMARY")],
        )
        second_household_collectors = second_household.individuals_and_roles.values_list(
            "individual__full_name", "role"
        )
        self.assertEqual(
            list(second_household_collectors),
            [("Test Testowski", "PRIMARY")],
        )

    @mock.patch(
        "hct_mis_api.apps.registration_datahub.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_handle_image_field(self) -> None:
        task = self.RdiKoboCreateTask()
        task.registration_data_import_mis = RegistrationDataImport()
        task.business_area = self.business_area
        task.attachments = [
            {
                "mimetype": "image/png",
                "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
                "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
                "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
                "filename": "wnosal/attachments/b83407aca1d647a5bf65a3383ee761d4/c09130af-6c9c-4dba-8c7f-1b2ff1970d19"
                "/signature-14_59_24.png",
                "instance": 102612403,
                "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
                "id": 35027752,
                "xform": 549831,
            },
            {
                "mimetype": "image/png",
                "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=xD"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-21_37.png",
                "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=xD"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-21_37.png",
                "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=xD"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-21_37.png",
                "filename": "wnosal/attachments/b83407aca1d647a5bf65a3383ee761d4/c09130af-6c9c-4dba-8c7f-1b2ff1970d19"
                "/signature-21_37_xDDD.png",
                "instance": 102612403,
                "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-21_37.png",
                "id": 35027752,
                "xform": 549831,
            },
        ]

        result = task._handle_image_field("image_is_not_there.gif", False)
        self.assertEqual(result, None)

        result = task._handle_image_field("signature-14_59_24.png", False)
        self.assertIsInstance(result, File)
        self.assertEqual(result.name, "signature-14_59_24.png", False)

        result = task._handle_image_field("signature-21_37.png", False)
        self.assertIsInstance(result, File)
        self.assertEqual(result.name, "signature-21_37.png", False)

    def test_handle_geopoint_field(self) -> None:
        geopoint = "51.107883 17.038538"
        task = self.RdiKoboCreateTask()

        expected = Point(x=51.107883, y=17.038538, srid=4326)
        result = task._handle_geopoint_field(geopoint, False)
        self.assertEqual(result, expected)

    def test_cast_and_assign(self) -> None:
        pass

    def test_cast_boolean_value(self) -> None:
        task = self.RdiKoboCreateTask()

        result = task._cast_value("FALSE", "estimated_birth_date_i_c")
        self.assertEqual(result, False)

        result = task._cast_value("false", "estimated_birth_date_i_c")
        self.assertEqual(result, False)

        result = task._cast_value("False", "estimated_birth_date_i_c")
        self.assertEqual(result, False)

        result = task._cast_value("0", "estimated_birth_date_i_c")
        self.assertEqual(result, False)

        result = task._cast_value("TRUE", "estimated_birth_date_i_c")
        self.assertEqual(result, True)

        result = task._cast_value("true", "estimated_birth_date_i_c")
        self.assertEqual(result, True)

        result = task._cast_value("True", "estimated_birth_date_i_c")
        self.assertEqual(result, True)

        result = task._cast_value("1", "estimated_birth_date_i_c")
        self.assertEqual(result, True)

        result = task._cast_value(True, "estimated_birth_date_i_c")
        self.assertEqual(result, True)

        result = task._cast_value(False, "estimated_birth_date_i_c")
        self.assertEqual(result, False)

    @mock.patch(
        "hct_mis_api.apps.registration_datahub.tasks.rdi_kobo_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_handle_documents_and_identities(self) -> None:
        task = self.RdiKoboCreateTask()
        task.registration_data_import_mis = RegistrationDataImport()
        task.business_area = self.business_area
        task.attachments = [
            {
                "mimetype": "image/png",
                "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
                "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
                "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
                "filename": "wnosal/attachments/b83407aca1d647a5bf65a3383ee761d4/c09130af-6c9c-4dba-8c7f-1b2ff1970d19"
                "/signature-14_59_24.png",
                "instance": 102612403,
                "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                "%2Fattachments%2Fb83407aca1d647a5bf65a3383ee761d4"
                "%2Fc09130af-6c9c-4dba-8c7f-1b2ff1970d19%2Fsignature-14_59_24.png",
                "id": 35027752,
                "xform": 549831,
            }
        ]
        individual = ImportedIndividualFactory()
        documents_and_identities = [
            {
                "birth_certificate": {
                    "number": "123123123",
                    "individual": individual,
                    "photo": "signature-14_59_24.png",
                    "issuing_country": Country("AFG"),
                }
            },
            {
                "national_passport": {
                    "number": "444111123",
                    "individual": individual,
                    "photo": "signature-14_59_24.png",
                    "issuing_country": Country("AFG"),
                }
            },
        ]
        task._handle_documents_and_identities(documents_and_identities)

        result = list(ImportedDocument.objects.values("document_number", "individual_id"))
        expected = [
            {"document_number": "123123123", "individual_id": individual.id},
            {"document_number": "444111123", "individual_id": individual.id},
        ]
        self.assertEqual(result, expected)

        photo = ImportedDocument.objects.first().photo
        self.assertIsInstance(photo, ImageFieldFile)
        self.assertTrue(photo.name.startswith("signature-14_59_24"))

        birth_certificate = ImportedDocument.objects.get(document_number=123123123).type.key
        national_passport = ImportedDocument.objects.get(document_number=444111123).type.key

        self.assertEqual(birth_certificate, "birth_certificate")
        self.assertEqual(national_passport, "national_passport")

    def _generate_huge_file(self) -> None:
        base_form = {
            "_notes": [],
            "household_questions/household_location/address_h_c": "Some Address 12",
            "household_questions/group_qo2zo48/f_0_5_age_group_h_c": "0",
            "monthly_income_questions/total_inc_h_f": "0",
            "household_questions/group_qo2zo48/m_6_11_age_group_h_c": "0",
            "household_questions/group_cu1lc89/m_6_11_disability_h_c": "0",
            "_xform_id_string": "ayp9jVNe5crcGerVjCjGj4",
            "_bamboo_dataset_id": "",
            "_tags": [],
            "household_questions/group_qo2zo48/pregnant_h_c": "0",
            "health_questions/pregnant_member_h_c": "0",
            "enumerator/name_enumerator": "Test",
            "monthly_expenditures_questions/total_expense_h_f": "0",
            "individual_questions": [
                {
                    "individual_questions/role_i_c": "primary",
                    "individual_questions/age": "65",
                    "individual_questions/more_information/marital_status_i_c": "single",
                    "individual_questions/more_information/id_type_i_c": "birth_certificate drivers_license",
                    "individual_questions/individual_index": "1",
                    "individual_questions/full_name_i_c": "Jan Kowalski",
                    "individual_questions/more_information/birth_certificate_photo_i_c": "test-11_53_20.png",
                    "individual_questions/relationship_i_c": "head",
                    "individual_questions/individual_vulnerabilities/work_status_i_c": "1",
                    "individual_questions/more_information/drivers_license_no_i_c": "ASD12367432Q",
                    "individual_questions/gender_i_c": "male",
                    "individual_questions/individual_vulnerabilities/disability_i_c": "not disabled",
                    "individual_questions/more_information/birth_certificate_no_i_c": "89671532",
                    "individual_questions/birth_date_i_c": "1955-07-28",
                }
            ],
            "household_questions/group_cu1lc89/f_12_17_disability_h_c": "0",
            "meta/instanceID": "uuid:84366d01-770a-42f0-b0f8-d498e35dd9e8",
            "household_questions/group_qo2zo48/f_12_17_age_group_h_c": "0",
            "end": "2020-06-18T12:05:31.700+02:00",
            "household_questions/group_qo2zo48/f_6_11_age_group_h_c": "0",
            "household_questions/group_cu1lc89/f_adults_disability_h_c": "0",
            "household_questions/group_qo2zo48/m_0_5_age_group_h_c": "0",
            "household_questions/group_qo2zo48/f_adults_h_c": "0",
            "household_questions/group_cu1lc89/m_adults_disability_h_c": "0",
            "start": "2020-06-15T11:49:14.246+02:00",
            "_attachments": [
                {
                    "mimetype": "image/png",
                    "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_31.png",
                    "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_31.png",
                    "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_31.png",
                    "filename": "wnosal/attachments/a716ab3cdfbc411aac9fa081874b6aa1/"
                    "2946bbb1-27fd-438a-b716-d864591808b2/test-11_53_31.png",
                    "instance": 104545171,
                    "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_31.png",
                    "id": 35910755,
                    "xform": 560567,
                },
                {
                    "mimetype": "image/png",
                    "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_20.png",
                    "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_20.png",
                    "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_20.png",
                    "filename": "wnosal/attachments/a716ab3cdfbc411aac9fa081874b6aa1/"
                    "2946bbb1-27fd-438a-b716-d864591808b2/test-11_53_20.png",
                    "instance": 104545171,
                    "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Ftest-11_53_20.png",
                    "id": 35910754,
                    "xform": 560567,
                },
                {
                    "mimetype": "image/png",
                    "download_small_url": "https://kc.humanitarianresponse.info/media/small?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Fsignature-11_53_11.png",
                    "download_large_url": "https://kc.humanitarianresponse.info/media/large?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Fsignature-11_53_11.png",
                    "download_url": "https://kc.humanitarianresponse.info/media/original?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Fsignature-11_53_11.png",
                    "filename": "wnosal/attachments/a716ab3cdfbc411aac9fa081874b6aa1/"
                    "2946bbb1-27fd-438a-b716-d864591808b2/signature-11_53_11.png",
                    "instance": 104545171,
                    "download_medium_url": "https://kc.humanitarianresponse.info/media/medium?media_file=wnosal"
                    "%2Fattachments%2Fa716ab3cdfbc411aac9fa081874b6aa1"
                    "%2F2946bbb1-27fd-438a-b716-d864591808b2%2Fsignature-11_53_11.png",
                    "id": 35910753,
                    "xform": 560567,
                },
            ],
            "_version_": "v8ia7fyHZNkkaUxuE28vDv",
            "_status": "submitted_via_web",
            "__version__": "vDTUHL6mTgLv2BPcBoRu5v",
            "meta/deprecatedID": "uuid:2946bbb1-27fd-438a-b716-d864591808b2",
            "wash_questions/total_liter_yesterday_h_f": "0",
            "food_security_questions/FCS_h_f": "NaN",
            "food_security_questions/cereals_tuber_score_h_f": "NaN",
            "_validation_status": {},
            "_uuid": "84366d01-770a-42f0-b0f8-d498e35dd9e8",
            "consent/consent_sign_h_c": "signature-11_53_11.png",
            "household_questions/household_location/country_h_c": "POL",
            "household_questions/group_cu1lc89/f_6_11_disability_h_c": "0",
            "_submitted_by": None,
            "household_questions/size_h_c": "1",
            "household_questions/group_cu1lc89/f_0_5_disability_h_c": "0",
            "household_questions/household_location/country_origin_h_c": "AFG",
            "household_questions/group_cu1lc89/m_0_5_disability_h_c": "0",
            "formhub/uuid": "a716ab3cdfbc411aac9fa081874b6aa1",
            "enumerator/group_fl9ht28/org_enumerator": "unicef",
            "household_questions/household_location/hh_geopoint_h_c": "51.106648 17.033256 0 0",
            "monthly_income_questions/round_total_income_h_f": "0",
            "_submission_time": "2020-06-15T09:54:07",
            "household_questions/household_location/residence_status_h_c": "refugee",
            "_geolocation": [51.106648, 17.033256],
            "monthly_expenditures_questions/round_total_expense_h_f": "0",
            "deviceid": "ee.humanitarianresponse.info:AqAb03KLuEfWXes0",
            "household_questions/group_qo2zo48/m_12_17_age_group_h_c": "0",
            "individual_questions_count": "1",
            "_id": 104545171,
            "household_questions/group_qo2zo48/m_adults_h_c": "1",
            "household_questions/group_cu1lc89/m_12_17_disability_h_c": "0",
        }

        result = []

        for _ in range(10000):
            copy: Dict = {**base_form}

            new_individuals = []
            for x in range(4):
                individual: Dict = {
                    **copy["individual_questions"][0],
                    "individual_questions/more_information/drivers_license_no_i_c": secrets.token_hex(15),
                    "individual_questions/more_information/birth_certificate_no_i_c": secrets.token_hex(15),
                    "individual_questions/relationship_i_c": "head" if x == 0 else "NON_BENEFICIARY",
                }
                new_individuals.append(individual)

            copy["individual_questions"] = new_individuals

            result.append(copy)

        with open(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/big_json.json",
            "w+",
        ) as json_file:
            json_file.write(json.dumps(result))

    def test_handle_household_dict(self) -> None:
        bank_accounts_to_create, households_to_create = [], []
        collectors_to_create, head_of_households_mapping, individuals_ids_hash_dict = dict(), dict(), dict()
        household = {
            "_id": 1111,
            "uuid": "qweqweqweqwe",
            "start": "2024-03",
            "end": "2024-03",
            "org_name_enumerator_h_c": "org_name_enumerator_string",
            "name_enumerator_h_c": "name_enumerator_string",
            "enumertor_phone_num_h_f": "321123123321",
            "consent_h_c": "1",
            "country_h_c": "NGA",
            "admin1_h_c": "NG037",
            "admin2_h_c": "NG037011",
            "village_h_c": "VillageName",
            "nearest_school_h_f": "next",
            "hh_geopoint_h_c": "46.123 6.312 0 0",
            "size_h_c": "5",
            "children_under_18_h_f": "2",
            "children_6_to_11_h_f": "1",
            "hohh_is_caregiver_h_f": "0",
            "alternate_collector": "1",
            "_xform_id_string": "kobo_asset_id_string_OR_detail_id",
            "_uuid": "123123-411d-85f1-123123",
            "_submission_time": "2022-02-22T12:22:22",
        }
        submission_meta_data = {
            "kobo_submission_uuid": "123123-411d-85f1-123123",
            "kobo_asset_id": "kobo_asset_id_string_OR_detail_id",
            "kobo_submission_time": "2022-02-22T12:22:22",
        }

        task = self.RdiKoboCreateTask()
        task.handle_household(
            bank_accounts_to_create,
            collectors_to_create,
            head_of_households_mapping,
            household,
            households_to_create,
            individuals_ids_hash_dict,
            self.registration_data_import,
            submission_meta_data,
        )
        hh = households_to_create[0]

        self.assertEqual(len(households_to_create), 1)
        self.assertEqual(hh.detail_id, "kobo_asset_id_string_OR_detail_id")
        self.assertEqual(hh.kobo_submission_time.isoformat(), "2022-02-22T12:22:22")
        self.assertEqual(hh.kobo_submission_uuid, "123123-411d-85f1-123123")
