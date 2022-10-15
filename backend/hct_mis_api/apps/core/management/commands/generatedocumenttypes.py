from django.core.management import BaseCommand
from django.db import transaction

from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_CHOICE, DocumentType
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocumentType as RDHDocumentType,
)


class Command(BaseCommand):
    help = "Generate document types for all countries"

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        identification_type_choice = tuple((doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE)
        document_types = []
        rdh_document_types = []
        for doc_type, label in identification_type_choice:
            document_types.append(DocumentType(label=label, type=doc_type))
            rdh_document_types.append(RDHDocumentType(label=label, type=doc_type))
        DocumentType.objects.bulk_create(document_types, ignore_conflicts=True)
        RDHDocumentType.objects.bulk_create(rdh_document_types, ignore_conflicts=True)
