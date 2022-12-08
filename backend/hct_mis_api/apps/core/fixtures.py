import factory
from faker import Faker

from hct_mis_api.apps.core.models import BusinessArea, StorageFile

faker = Faker()


def create_afghanistan(
    is_payment_plan_applicable=False,
    approval_number_required=2,
    authorization_number_required=2,
    finance_review_number_required=3,
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
            "approval_number_required": approval_number_required,
            "authorization_number_required": authorization_number_required,
            "finance_review_number_required": finance_review_number_required,
            "is_payment_plan_applicable": is_payment_plan_applicable,
        },
    )


class StorageFileFactory(factory.DjangoModelFactory):
    class Meta:
        model = StorageFile

    business_area = factory.LazyAttribute(lambda _: BusinessArea.objects.first())
