from django.test import TestCase

from django_countries.fields import Country

from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
from hct_mis_api.apps.registration_datahub.models import ImportedDocumentType


class TestImportedDocumentTypeModel(TestCase):
    databases = "__all__"

    def test_create_document_type_with_specific_country(self):
        document_type = ImportedDocumentType.objects.create(
            country=Country(code="PL"), type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
        )
        self.assertEqual(document_type.country, Country(code="PL"))

    def test_create_document_type_without_specific_country(self):
        document_type = ImportedDocumentType.objects.create(
            type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
        )
        self.assertEqual(document_type.country, Country(code="U"))
