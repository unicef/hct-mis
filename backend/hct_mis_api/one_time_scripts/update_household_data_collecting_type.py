from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.core.models import BusinessArea



def update_household_data_collecting_type():
    for business_area in BusinessArea.objects.all():
        print(f"Updating Households data_collecting_type for BA: {business_area.name}")

        for program in Program.objects.filter(business_area=business_area, data_collecting_type__isnull=False):
            data_collecting_type = program.data_collecting_type
            for target_population in TargetPopulation.objects.filter(program=program):
                Household.objects.filter(target_populations=target_population, data_collecting_type__isnull=True).update(data_collecting_type=data_collecting_type)

