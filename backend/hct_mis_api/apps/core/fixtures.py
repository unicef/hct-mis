from typing import Any, List

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType, StorageFile

faker = Faker()


def create_afghanistan(
    is_payment_plan_applicable: bool = False,
) -> BusinessArea:
    return BusinessArea.objects.get_or_create(
        code="0060",
        defaults={
            "code": "0060",
            "name": "Afghanistan",
            "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            "region_code": "64",
            "region_name": "SAR",
            "slug": "afghanistan",
            "has_data_sharing_agreement": True,
            "is_payment_plan_applicable": is_payment_plan_applicable,
            "kobo_token": "XXX",
        },
    )[0]


def create_ukraine(
    is_payment_plan_applicable: bool = False,
) -> BusinessArea:
    return BusinessArea.objects.create(
        **{
            "code": "4410",
            "name": "Ukraine",
            "long_name": "UKRAINE",
            "region_code": "66",
            "region_name": "ECAR",
            "slug": "ukraine",
            "has_data_sharing_agreement": True,
            "is_payment_plan_applicable": is_payment_plan_applicable,
            "kobo_token": "YYY",
        }
    )


def create_kenya(
    is_payment_plan_applicable: bool = False,
) -> BusinessArea:
    return BusinessArea.objects.create(
        **{
            "code": "2400",
            "name": "Kenya",
            "long_name": "THE REPUBLIC OF KENYA",
            "region_code": "63",
            "region_name": "ESAR",
            "slug": "kenya",
            "has_data_sharing_agreement": True,
            "is_payment_plan_applicable": is_payment_plan_applicable,
            "kobo_token": "ZZZ",
        }
    )


class StorageFileFactory(DjangoModelFactory):
    class Meta:
        model = StorageFile

    business_area = factory.LazyAttribute(lambda _: BusinessArea.objects.first())


def generate_data_collecting_types() -> None:
    data_collecting_types = [
        {"label": "Partial", "code": "partial_individuals", "description": "Partial individuals collected"},
        {"label": "Full", "code": "full_collection", "description": "Full individual collected"},
        {"label": "Size only", "code": "size_only", "description": "Size only collected"},
        {
            "label": "size/age/gender disaggregated",
            "code": "size_age_gender_disaggregated",
            "description": "No individual data",
        },
    ]

    for data_dict in data_collecting_types:
        DataCollectingType.objects.update_or_create(**data_dict)


class DataCollectingTypeFactory(DjangoModelFactory):
    class Meta:
        model = DataCollectingType
        django_get_or_create = ("label", "code")

    label = factory.Faker("text", max_nb_chars=30)
    code = factory.Faker("text", max_nb_chars=30)
    type = DataCollectingType.Type.STANDARD
    description = factory.Faker("sentence", nb_words=6, variable_nb_words=True, ext_word_list=None)
    individual_filters_available = True
    household_filters_available = True

    @factory.post_generation
    def business_areas(self, create: Any, extracted: List[Any], **kwargs: Any) -> None:
        if not create:
            return

        if extracted:
            for business_area in extracted:
                self.limit_to.add(business_area)
