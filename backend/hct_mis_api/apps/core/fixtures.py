import factory
from faker import Faker

from hct_mis_api.apps.core.models import BusinessArea, StorageFile

faker = Faker()


def create_afghanistan(
    is_payment_plan_applicable: bool = False,
) -> BusinessArea:
    return BusinessArea.objects.create(
        **{
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
    )


class StorageFileFactory(factory.DjangoModelFactory):
    class Meta:
        model = StorageFile

    business_area = factory.LazyAttribute(lambda _: BusinessArea.objects.first())
