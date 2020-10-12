import json
import os
import secrets
import time
import unittest
from datetime import date
from io import BytesIO
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.files import File
from django.core.management import call_command
from django.db.models.fields.files import ImageFieldFile
from django.forms import model_to_dict
from django.test import TestCase

from django_countries.fields import Country
from PIL import Image

from core.models import AdminArea, AdminAreaType, BusinessArea
from registration_data.fixtures import RegistrationDataImportFactory
from registration_datahub.fixtures import ImportedIndividualFactory, RegistrationDataImportDatahubFactory
from registration_datahub.models import (
    ImportData,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
)


class ImageLoaderMock:
    def image_in(self, *args, **kwargs):
        return True

    def get(self, *args, **kwargs):
        content = Path(f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/image.png").read_bytes()
        file = File(BytesIO(content), name="image.png")
        return Image.open(file)


class CellMock:
    def __init__(self, value, coordinate):
        self.value = value
        self.coordinate = coordinate


class TestRdiCreateTask(TestCase):
    multi_db = True

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")
        from registration_datahub.tasks.rdi_create import RdiKoboCreateTask, RdiXlsxCreateTask

        cls.RdiXlsxCreateTask = RdiXlsxCreateTask
        cls.RdiKoboCreateTask = RdiKoboCreateTask

        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests" "/test_file/new_reg_data_import.xlsx"
        ).read_bytes()
        file = File(BytesIO(content), name="new_reg_data_import.xlsx")
        business_area = BusinessArea.objects.first()
        cls.import_data = ImportData.objects.create(
            file=file,
            number_of_households=3,
            number_of_individuals=6,
        )
        cls.registration_data_import = RegistrationDataImportDatahubFactory(
            import_data=cls.import_data, business_area_slug=business_area.slug, hct_id=None
        )
        hct_rdi = RegistrationDataImportFactory(
            datahub_id=cls.registration_data_import.id,
            name=cls.registration_data_import.name,
            business_area=business_area,
        )
        cls.registration_data_import.hct_id = hct_rdi.id
        cls.registration_data_import.save()
        cls.business_area = BusinessArea.objects.first()

    def test_execute(self):
        task = self.RdiXlsxCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
        )

        households_count = ImportedHousehold.objects.count()
        individuals_count = ImportedIndividual.objects.count()

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
        }
        matching_individuals = ImportedIndividual.objects.filter(**individual_data)

        self.assertEqual(matching_individuals.count(), 1)

        household_data = {
            "residence_status": "REFUGEE",
            "country": "AF",
            "flex_fields": {},
        }
        household = matching_individuals.first().household
        household_obj_data = model_to_dict(household, ("residence_status", "country", "flex_fields"))

        roles = household.individuals_and_roles.all()
        self.assertEqual(roles.count(), 1)
        role = roles.first()
        self.assertEqual(role.role, "PRIMARY")
        self.assertEqual(role.individual.full_name, "Some Full Name")

        self.assertEqual(household_obj_data, household_data)

    def test_handle_document_fields(self):
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
            "individual_14_birth_certificate_no_i_c": {
                "individual": individual,
                "name": "Birth Certificate",
                "type": "BIRTH_CERTIFICATE",
                "value": value,
            }
        }
        self.assertEqual(task.documents, expected)

        # other_id_type_i_c
        number = "CD1247246Q12W"
        name = "Some Doc"
        header = "other_id_type_i_c"
        task._handle_document_fields(
            name,
            header,
            row_num,
            individual,
        )
        expected = {
            "individual_14_birth_certificate_no_i_c": {
                "individual": individual,
                "name": "Birth Certificate",
                "type": "BIRTH_CERTIFICATE",
                "value": value,
            },
            "individual_14_other": {"individual": individual, "name": name, "type": "OTHER"},
        }
        self.assertEqual(task.documents, expected)
        # other_id_no_i_c
        header = "other_id_no_i_c"
        task._handle_document_fields(
            number,
            header,
            row_num,
            individual,
        )
        expected = {
            "individual_14_birth_certificate_no_i_c": {
                "individual": individual,
                "name": "Birth Certificate",
                "type": "BIRTH_CERTIFICATE",
                "value": value,
            },
            "individual_14_other": {"individual": individual, "name": name, "type": "OTHER", "value": number},
        }
        self.assertEqual(task.documents, expected)

    @mock.patch(
        "registration_datahub.tasks.rdi_create.SheetImageLoader",
        ImageLoaderMock,
    )
    @mock.patch(
        "registration_datahub.tasks.rdi_create.timezone.now",
        lambda: "2020-06-22 12:00",
    )
    def test_handle_document_photo_fields(self):
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
        expected = {
            "individual_14_birth_certificate_no_i_c": {"individual": individual, "photo": f"12-2020-06-22 12:00.jpg"}
        }
        self.assertEqual(task.documents, expected)

        birth_cert_doc = {
            "individual_14_birth_certificate_no_i_c": {
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
        expected = {
            "individual_14_birth_certificate_no_i_c": {
                **birth_cert_doc["individual_14_birth_certificate_no_i_c"],
                "photo": f"12-2020-06-22 12:00.jpg",
            }
        }
        self.assertEqual(task.documents, expected)

    def test_handle_geopoint_field(self):
        empty_geopoint = ""
        valid_geopoint = "51.107883, 17.038538"
        task = self.RdiXlsxCreateTask()

        result = task._handle_geopoint_field(empty_geopoint)
        self.assertEqual(result, "")

        expected = Point(x=51.107883, y=17.038538, srid=4326)
        result = task._handle_geopoint_field(valid_geopoint)
        self.assertEqual(result, expected)

    def test_create_documents(self):
        task = self.RdiXlsxCreateTask()
        individual = ImportedIndividualFactory()
        content = Path(f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/image.png").read_bytes()
        image = File(BytesIO(content), name="image.png")
        task.business_area = self.business_area
        doc_type = ImportedDocumentType.objects.create(
            country="AF",
            label="Birth Certificate",
            type="BIRTH_CERTIFICATE",
        )
        task.documents = {
            "individual_14_birth_certificate_no_i_c": {
                "individual": individual,
                "name": "Birth Certificate",
                "type": "BIRTH_CERTIFICATE",
                "value": "CD1247246Q12W",
                "photo": image,
            }
        }
        task._create_documents()

        documents = ImportedDocument.objects.values("document_number", "type_id")
        self.assertEqual(documents.count(), 1)

        expected = [{"document_number": "CD1247246Q12W", "type_id": doc_type.id}]
        self.assertEqual(list(documents), expected)

        document = ImportedDocument.objects.first()
        photo = document.photo.name
        self.assertTrue(photo.startswith("image_") and photo.endswith(".png"))

    def test_cast_value(self):
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


class TestRdiKoboCreateTask(TestCase):
    multi_db = True

    @staticmethod
    def _return_test_image(*args, **kwargs):
        return BytesIO(
            Path(f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/image.png").read_bytes()
        )

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")
        from registration_datahub.tasks.rdi_create import RdiKoboCreateTask, RdiXlsxCreateTask

        cls.RdiXlsxCreateTask = RdiXlsxCreateTask
        cls.RdiKoboCreateTask = RdiKoboCreateTask

        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests" "/test_file/kobo_submissions.json"
        ).read_bytes()
        file = File(BytesIO(content), name="kobo_submissions.json")
        cls.import_data = ImportData.objects.create(
            file=file,
            number_of_households=1,
            number_of_individuals=2,
        )

        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests" "/test_file/kobo_submissions_collectors.json"
        ).read_bytes()
        file = File(BytesIO(content), name="kobo_submissions_collectors.json")
        cls.import_data_collectors = ImportData.objects.create(
            file=file,
            number_of_households=2,
            number_of_individuals=5,
        )

        cls.business_area = BusinessArea.objects.first()
        cls.business_area.kobo_token = "1234ABC"
        cls.business_area.save()

        admin1_type = AdminAreaType.objects.create(name="Bakool", admin_level=1, business_area=cls.business_area)
        admin1 = AdminArea.objects.create(title="SO25", admin_area_type=admin1_type)

        admin2_type = AdminAreaType.objects.create(name="Ceel Barde", admin_level=2, business_area=cls.business_area)
        AdminArea.objects.create(title="SO2502", parent=admin1, admin_area_type=admin2_type)

        cls.registration_data_import = RegistrationDataImportDatahubFactory(
            import_data=cls.import_data, business_area_slug=cls.business_area.slug
        )
        hct_rdi = RegistrationDataImportFactory(
            datahub_id=cls.registration_data_import.id,
            name=cls.registration_data_import.name,
            business_area=cls.business_area,
        )
        cls.registration_data_import.hct_id = hct_rdi.id
        cls.registration_data_import.save()

    @mock.patch(
        "registration_datahub.tasks.rdi_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_execute(self):
        task = self.RdiKoboCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data.id,
            self.business_area.id,
        )

        households = ImportedHousehold.objects.all()
        individuals = ImportedIndividual.objects.all()

        self.assertEqual(1, households.count())
        self.assertEqual(2, individuals.count())

        individual = individuals.get(full_name="Test Testowski")

        individuals_obj_data = model_to_dict(
            individual,
            ("country", "sex", "age", "marital_status", "relationship"),
        )
        expected = {
            "relationship": "HEAD",
            "sex": "MALE",
            "marital_status": "MARRIED",
        }
        self.assertEqual(individuals_obj_data, expected)

        household_obj_data = model_to_dict(individual.household, ("residence_status", "country", "flex_fields"))
        expected = {
            "residence_status": "REFUGEE",
            "country": Country(code="AF"),
            "flex_fields": {},
        }
        self.assertEqual(household_obj_data, expected)

    @mock.patch(
        "registration_datahub.tasks.rdi_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_execute_multiple_collectors(self):
        task = self.RdiKoboCreateTask()
        task.execute(
            self.registration_data_import.id,
            self.import_data_collectors.id,
            self.business_area.id,
        )
        households = ImportedHousehold.objects.all()
        individuals = ImportedIndividual.objects.all()

        self.assertEqual(households.count(), 2)
        self.assertEqual(individuals.count(), 4)

        documents = ImportedDocument.objects.values_list("individual__full_name", flat=True)
        self.assertEqual(
            sorted(list(documents)),
            ["Tesa Testowski", "Test Testowski", "Zbyszek Zbyszkowski", "abc efg"],
        )

        first_household = households.get(size=3)
        second_household = households.get(size=1)

        first_household_collectors = first_household.individuals_and_roles.values_list("individual__full_name", "role")
        self.assertEqual(
            list(first_household_collectors),
            [("Tesa Testowski", "ALTERNATE"), ("Test Testowski", "PRIMARY")],
        )
        second_household_collectors = second_household.individuals_and_roles.values_list(
            "individual__full_name", "role"
        )
        self.assertEqual(
            list(second_household_collectors),
            [("Test Testowski", "PRIMARY")],
        )

    @mock.patch(
        "registration_datahub.tasks.rdi_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_handle_image_field(self):
        task = self.RdiKoboCreateTask()
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

        result = task._handle_image_field("image_is_not_there.gif")
        self.assertEqual(result, "")

        result = task._handle_image_field("signature-14_59_24.png")
        self.assertIsInstance(result, File)
        self.assertEqual(result.name, "signature-14_59_24.png")

    def test_handle_geopoint_field(self):
        geopoint = "51.107883 17.038538"
        task = self.RdiKoboCreateTask()

        expected = Point(x=51.107883, y=17.038538, srid=4326)
        result = task._handle_geopoint_field(geopoint)
        self.assertEqual(result, expected)

    def test_cast_and_assign(self):
        pass

    @mock.patch(
        "registration_datahub.tasks.rdi_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    def test_handle_documents_and_identities(self):
        task = self.RdiKoboCreateTask()
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
        individuals_dict = {individual.get_hash_key: individual}
        documents_and_identities = [
            {
                "birth_certificate": {
                    "number": "123123123",
                    "individual": individual,
                    "photo": "signature-14_59_24.png",
                }
            },
            {
                "national_passport": {
                    "number": "444111123",
                    "individual": individual,
                    "photo": "signature-14_59_24.png",
                }
            },
        ]
        task._handle_documents_and_identities(documents_and_identities, individuals_dict)

        result = list(ImportedDocument.objects.values("document_number", "individual_id"))
        expected = [
            {"document_number": "123123123", "individual_id": individual.id},
            {"document_number": "444111123", "individual_id": individual.id},
        ]
        self.assertEqual(result, expected)

        photo = ImportedDocument.objects.first().photo
        self.assertIsInstance(photo, ImageFieldFile)
        self.assertTrue(photo.name.startswith("signature-14_59_24"))

        birth_certificate = ImportedDocument.objects.get(document_number=123123123).type.type
        national_passport = ImportedDocument.objects.get(document_number=444111123).type.type

        self.assertEqual(birth_certificate, "BIRTH_CERTIFICATE")
        self.assertEqual(national_passport, "NATIONAL_PASSPORT")

    @mock.patch(
        "registration_datahub.tasks.rdi_create.KoboAPI.get_attached_file",
        _return_test_image,
    )
    @unittest.skip("Remove this and run manually only!")
    def test_performance(self):
        from registration_datahub.validators import KoboProjectImportDataValidator

        self._generate_huge_file()
        content = Path(
            f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests" "/test_file/big_json.json"
        ).read_bytes()
        file = File(BytesIO(content), name="big_json.json")
        import_data = ImportData.objects.create(
            file=file,
            number_of_households=1,
            number_of_individuals=2,
        )
        registration_data_import = RegistrationDataImportDatahubFactory(import_data=import_data)
        start = time.process_time()
        errors = KoboProjectImportDataValidator.validate_fields(
            json.loads(import_data.file.read().decode()),
            self.business_area.name,
        )
        self.assertEqual(errors, [])

        task = self.RdiKoboCreateTask()
        task.execute(
            registration_data_import.id,
            import_data.id,
            self.business_area.id,
        )
        end = time.process_time() - start
        execution_time = f"{end:.2f} seconds"
        print(execution_time)
        os.remove(f"{settings.PROJECT_ROOT}/apps/registration_datahub/tests/test_file/big_json.json")

    def _generate_huge_file(self):
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
            "household_questions/group_qo2zo48/f_pregnant_h_c": "0",
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
                    "individual_questions/individual_vulnerabilities/work_status_i_c": "YES",
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

        for i in range(10000):
            copy = {**base_form}

            new_individuals = []
            for x in range(4):
                individual = {
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
