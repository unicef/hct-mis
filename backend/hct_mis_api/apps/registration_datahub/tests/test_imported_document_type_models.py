from django.test import TestCase

from hct_mis_api.apps.core.base_test_case import TimeMeasuringTestCase
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
from hct_mis_api.apps.registration_datahub.models import ImportedDocumentType


class TestImportedDocumentTypeModel(TestCase, TimeMeasuringTestCase):
    databases = "__all__"

    def test_create_document_type(self) -> None:
        assert ImportedDocumentType.objects.create(type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE)
