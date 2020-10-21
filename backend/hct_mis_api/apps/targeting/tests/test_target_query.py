from django.core.management import call_command

from targeting.models import (
    HouseholdSelection,
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetingCriteriaRuleFilter,
    TargetPopulation,
)

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea
from household.fixtures import create_household


class TestTargetPopulationQuery(APITestCase):
    ALL_TARGET_POPULATION_QUERY = """
            query AllTargetPopulation($finalListTotalHouseholdsMin: Int) {
                allTargetPopulation(finalListTotalHouseholdsMin:$finalListTotalHouseholdsMin) {
                    edges {
                        node {
                             name
                             status
                            candidateListTotalHouseholds
                            candidateListTotalIndividuals
                            finalListTotalHouseholds
                            finalListTotalIndividuals
                        }
                    }
                }
            }
            """
    TARGET_POPULATION_QUERY = """
       query TargetPopulation($id:ID!) {
          targetPopulation(id:$id){
            name
            status
            candidateListTotalHouseholds
            candidateListTotalIndividuals
            finalListTotalHouseholds
            finalListTotalIndividuals
            candidateListTargetingCriteria{
              rules{
                filters{
                  comparisionMethod
                  fieldName
                  isFlexField
                  arguments
                  fieldAttribute{
                    labelEn
                    type
                  }
                }
              }
            }
            finalListTargetingCriteria{
              rules{
                filters{
                  comparisionMethod
                  fieldName
                  isFlexField
                  arguments
                }
              }
            }
          }
        }
                """

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")
        business_area = BusinessArea.objects.first()
        _ = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": business_area},
        )
        (household, individuals) = create_household(
            {"size": 1, "residence_status": "HOST", "business_area": business_area},
        )
        cls.household_size_1 = household
        cls.household_residence_status_citizen = cls.household_size_1
        (household, individuals) = create_household(
            {"size": 2, "residence_status": "REFUGEE", "business_area": business_area},
        )
        cls.household_residence_status_refugee = household
        cls.household_size_2 = cls.household_residence_status_refugee

        cls.user = UserFactory.create()
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [2], "comparision_method": "EQUALS"}
        )
        cls.target_population_size_2 = TargetPopulation(
            name="target_population_size_2",
            created_by=cls.user,
            candidate_list_targeting_criteria=targeting_criteria,
        )
        cls.target_population_size_2.save()
        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "residence_status", "arguments": ["REFUGEE"], "comparision_method": "EQUALS"}
        )
        cls.target_population_residence_status = TargetPopulation(
            name="target_population_residence_status",
            created_by=cls.user,
            candidate_list_targeting_criteria=targeting_criteria,
        )
        cls.target_population_residence_status.save()

        targeting_criteria = cls.get_targeting_criteria_for_rule(
            {"field_name": "size", "arguments": [1], "comparision_method": "EQUALS"}
        )
        cls.target_population_size_1_approved = TargetPopulation(
            name="target_population_size_1_approved",
            created_by=cls.user,
            candidate_list_targeting_criteria=targeting_criteria,
            status=TargetPopulation.STATUS_APPROVED,
        )
        cls.target_population_size_1_approved.save()
        HouseholdSelection.objects.create(
            household=cls.household_size_1,
            target_population=cls.target_population_size_1_approved,
        )

    @staticmethod
    def get_targeting_criteria_for_rule(rule_filter):
        targeting_criteria = TargetingCriteria()
        targeting_criteria.save()
        rule = TargetingCriteriaRule(targeting_criteria=targeting_criteria)
        rule.save()
        rule_filter = TargetingCriteriaRuleFilter(**rule_filter, targeting_criteria_rule=rule)
        rule_filter.save()
        return targeting_criteria

    def test_simple_all_targets_query(self):
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.ALL_TARGET_POPULATION_QUERY,
        )

    def test_simple_all_targets_query_filter_finalListTotalHouseholdsMin(self):
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.ALL_TARGET_POPULATION_QUERY,
            variables={"finalListTotalHouseholdsMin": 1},
        )

    def test_simple_target_query(self):
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.TARGET_POPULATION_QUERY,
            variables={
                "id": self.id_to_base64(
                    self.target_population_size_1_approved.id,
                    "TargetPopulation",
                )
            },
        )

    def test_simple_target_query_2(self):
        self.snapshot_graphql_request(
            request_string=TestTargetPopulationQuery.TARGET_POPULATION_QUERY,
            variables={
                "id": self.id_to_base64(
                    self.target_population_residence_status.id,
                    "TargetPopulation",
                )
            },
        )
