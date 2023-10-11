import os
from typing import Any

from django.core.files.base import ContentFile

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceDocument
from hct_mis_api.apps.household.models import Document, Household, Individual


def migrate_files_to_representations(business_area: BusinessArea) -> None:
    migrate_grievance_document_files(business_area)
    migrate_document_files(business_area)
    migrate_individual_files(business_area)
    migrate_household_files(business_area)


def copy_file(instance: Any, file_field: str) -> None:
    name_and_extension = os.path.splitext(getattr(instance, file_field).name)
    new_file = ContentFile(getattr(instance, file_field).read())
    new_file.name = f"{name_and_extension[0]}{instance.id}{name_and_extension[1]}"
    setattr(instance, file_field, new_file)
    instance.save()


def migrate_grievance_document_files(business_area: BusinessArea) -> None:
    for grievance_document in GrievanceDocument.objects.filter(
        grievance_ticket__is_original=False,
        grievance_ticket__business_area=business_area,
    ):
        if grievance_document.file:
            copy_file(grievance_document, "file")


def migrate_document_files(business_area: BusinessArea) -> None:
    for document in Document.original_and_repr_objects.filter(
        individual__business_area=business_area,
        copied_from__isnull=False,
    ):
        if document.photo:
            copy_file(document, "photo")


def migrate_individual_files(business_area: BusinessArea) -> None:
    for individual in Individual.original_and_repr_objects.filter(
        is_original=False,
        business_area=business_area,
    ):
        if individual.photo:
            copy_file(individual, "photo")
        if individual.disability_certificate_picture:
            copy_file(individual, "disability_certificate_picture")


def migrate_household_files(business_area: BusinessArea) -> None:
    for household in Household.original_and_repr_objects.filter(
        is_original=False,
        business_area=business_area,
    ):
        if household.consent_sign:
            copy_file(household, "consent_sign")
