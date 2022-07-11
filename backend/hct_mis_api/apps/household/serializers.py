from rest_framework import serializers
from django.utils import timezone

from hct_mis_api.apps.targeting.models import HouseholdSelection, TargetPopulation
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual, ImportedHousehold
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.household.models import Individual, Household


def get_household_status(household):
    if isinstance(household, Household):
        payment_records = PaymentRecord.objects.filter(household=household)
        if payment_records.exists():
            return "paid", payment_records.first().updated_at

        selections = HouseholdSelection.objects.filter(household=household)
        if selections.exists():
            selection = selections.order_by("updated_at").first()
            if selection.target_population.status == TargetPopulation.STATUS_PROCESSING:
                return "sent to cash assist", timezone.now()
            return "targeted", selection.updated_at

        return "merged to population", household.created_at

    # if is not Household, then must be ImportedHousehold, so it was imported
    return "imported", household.updated_at


def get_individual_info(individual, tax_id):
    return {
        "role": individual.role,
        "relationship": individual.relationship,
        "tax_id": tax_id,
    }


def get_household_info(household, individual=None, tax_id=None):
    status, date = get_household_status(household)
    output = {"status": status, "date": date}
    if individual:
        output["individual"] = get_individual_info(individual, tax_id=tax_id)
    return {"info": output}


def serialize_by_individual(individual, tax_id):
    return get_household_info(individual.household, individual, tax_id)


def serialize_by_household(household):
    return get_household_info(household)
