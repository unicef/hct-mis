import json

from hct_mis_api.apps.payment.fixtures import FinancialServiceProviderFactory
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.household.fixtures import IndividualRoleInHouseholdFactory
from hct_mis_api.apps.targeting.fixtures import TargetPopulationFactory, TargetingCriteriaFactory
from hct_mis_api.apps.payment.fixtures import PaymentChannelFactory
from hct_mis_api.apps.payment.models import GenericPayment
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import HEAD, MALE
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.models import TargetPopulation


def base_setup(cls):
    create_afghanistan()
    cls.business_area = BusinessArea.objects.get(slug="afghanistan")
    cls.user = UserFactory.create()
    cls.create_user_role_with_permissions(
        cls.user,
        [Permissions.PAYMENT_MODULE_CREATE, Permissions.PAYMENT_MODULE_VIEW_DETAILS],
        BusinessArea.objects.get(slug="afghanistan"),
    )

    cls.registration_data_import = RegistrationDataImportFactory(business_area=cls.business_area)

    cls.household_1, cls.individuals_1 = create_household_and_individuals(
        household_data={
            "registration_data_import": cls.registration_data_import,
            "business_area": cls.business_area,
        },
        individuals_data=[{}],
    )
    PaymentChannelFactory(
        individual=cls.individuals_1[0],
        delivery_mechanism=GenericPayment.DELIVERY_TYPE_VOUCHER,
    )
    PaymentChannelFactory(
        individual=cls.individuals_1[0],
        delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
    )
    IndividualRoleInHouseholdFactory(
        individual=cls.individuals_1[0],
        household=cls.household_1,
        role=ROLE_PRIMARY,
    )

    cls.household_2, cls.individuals_2 = create_household_and_individuals(
        household_data={
            "registration_data_import": cls.registration_data_import,
            "business_area": cls.business_area,
        },
        individuals_data=[{}],
    )
    PaymentChannelFactory(
        individual=cls.individuals_2[0],
        delivery_mechanism=GenericPayment.DELIVERY_TYPE_TRANSFER,
    )
    PaymentChannelFactory(
        individual=cls.individuals_2[0],
        delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
    )
    IndividualRoleInHouseholdFactory(
        individual=cls.individuals_2[0],
        household=cls.household_2,
        role=ROLE_PRIMARY,
    )

    cls.household_3, cls.individuals_3 = create_household_and_individuals(
        household_data={
            "registration_data_import": cls.registration_data_import,
            "business_area": cls.business_area,
        },
        individuals_data=[{}],
    )
    IndividualRoleInHouseholdFactory(
        individual=cls.individuals_3[0],
        household=cls.household_3,
        role=ROLE_PRIMARY,
    )
    PaymentChannelFactory(
        individual=cls.individuals_3[0],
        delivery_mechanism=GenericPayment.DELIVERY_TYPE_TRANSFER,
    )
    PaymentChannelFactory(
        individual=cls.individuals_3[0],
        delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
    )


def payment_plan_setup(cls):
    target_population = TargetPopulationFactory(
        created_by=cls.user,
        candidate_list_targeting_criteria=(TargetingCriteriaFactory()),
        business_area=cls.business_area,
        status=TargetPopulation.STATUS_LOCKED,
    )
    target_population.apply_criteria_query()  # simulate having TP households calculated
    cls.payment_plan = PaymentPlanFactory(
        total_households_count=3, target_population=target_population, status=PaymentPlan.Status.LOCKED
    )
    cls.encoded_payment_plan_id = encode_id_base64(cls.payment_plan.id, "PaymentPlan")

    cls.santander_fsp = FinancialServiceProviderFactory(
        name="Santander", delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER], distribution_limit=None
    )
    cls.encoded_santander_fsp_id = encode_id_base64(cls.santander_fsp.id, "FinancialServiceProvider")

    cls.bank_of_america_fsp = FinancialServiceProviderFactory(
        name="Bank of America", delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_VOUCHER], distribution_limit=1000
    )
    cls.encoded_bank_of_america_fsp_id = encode_id_base64(cls.bank_of_america_fsp.id, "FinancialServiceProvider")

    cls.bank_of_europe_fsp = FinancialServiceProviderFactory(
        name="Bank of Europe",
        delivery_mechanisms=[GenericPayment.DELIVERY_TYPE_VOUCHER, GenericPayment.DELIVERY_TYPE_TRANSFER],
        distribution_limit=50000,
    )
    cls.encoded_bank_of_europe_fsp_id = encode_id_base64(cls.bank_of_europe_fsp.id, "FinancialServiceProvider")


ASSIGN_FSPS_MUTATION = """
mutation AssignFspToDeliveryMechanism($paymentPlanId: ID!, $mappings: [FSPToDeliveryMechanismMappingInput!]!) {
    assignFspToDeliveryMechanism(input: {
        paymentPlanId: $paymentPlanId,
        mappings: $mappings
    }) {
        paymentPlan {
            id
            deliveryMechanisms {
                name
                order
                fsp {
                    id
                }
            }
        }
    }
}
"""

CHOOSE_DELIVERY_MECHANISMS_MUTATION = """
mutation ChooseDeliveryMechanismsForPaymentPlan($input: ChooseDeliveryMechanismsForPaymentPlanInput!) {
  chooseDeliveryMechanismsForPaymentPlan(input: $input) {
    paymentPlan {
      id
      deliveryMechanisms {
        order
        name
      }
    }
  }
}
"""

CURRENT_PAYMENT_PLAN_QUERY = """
query PaymentPlan($id: ID!) {
    paymentPlan(id: $id) {
        id
        deliveryMechanisms {
            name
            order
            fsp {
                id
            }
        }
    }
}
"""


class TestFSPSetup(APITestCase):
    @classmethod
    def setUpTestData(cls):
        base_setup(cls)

    def test_choosing_delivery_mechanism_order(self):
        payment_plan = PaymentPlanFactory(total_households_count=1, status=PaymentPlan.Status.LOCKED)
        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        choose_dms_mutation_variables_mutation_variables_without_delivery_mechanisms = dict(
            input=dict(
                paymentPlanId=encoded_payment_plan_id,
                deliveryMechanisms=[],
            )
        )
        response_without_mechanisms = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=choose_dms_mutation_variables_mutation_variables_without_delivery_mechanisms,
        )
        assert response_without_mechanisms is not None and "data" in response_without_mechanisms
        payment_plan_without_delivery_mechanisms = response_without_mechanisms["data"][
            "chooseDeliveryMechanismsForPaymentPlan"
        ]["paymentPlan"]
        self.assertEqual(payment_plan_without_delivery_mechanisms["id"], encoded_payment_plan_id)
        self.assertEqual(payment_plan_without_delivery_mechanisms["deliveryMechanisms"], [])

        response_with_wrong_mechanism = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=encoded_payment_plan_id,
                    deliveryMechanisms=[""],  # empty string is invalid
                )
            ),
        )
        assert "errors" in response_with_wrong_mechanism, response_with_wrong_mechanism
        self.assertEqual(
            response_with_wrong_mechanism["errors"][0]["message"],
            "Delivery mechanism '' is not valid.",
        )

        choose_dms_mutation_variables_mutation_variables_with_delivery_mechanisms = dict(
            input=dict(
                paymentPlanId=encoded_payment_plan_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_VOUCHER],
            )
        )
        response_with_mechanisms = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=choose_dms_mutation_variables_mutation_variables_with_delivery_mechanisms,
        )
        assert response_with_mechanisms is not None and "data" in response_with_mechanisms
        payment_plan_with_delivery_mechanisms = response_with_mechanisms["data"][
            "chooseDeliveryMechanismsForPaymentPlan"
        ]["paymentPlan"]
        self.assertEqual(payment_plan_with_delivery_mechanisms["id"], encoded_payment_plan_id)
        self.assertEqual(
            payment_plan_with_delivery_mechanisms["deliveryMechanisms"][0],
            {"name": GenericPayment.DELIVERY_TYPE_TRANSFER, "order": 1},
        )
        self.assertEqual(
            payment_plan_with_delivery_mechanisms["deliveryMechanisms"][1],
            {"name": GenericPayment.DELIVERY_TYPE_VOUCHER, "order": 2},
        )

    def test_being_able_to_get_possible_delivery_mechanisms(self):
        query = """
query AllDeliveryMechanisms {
    allDeliveryMechanisms {
        name
        value
    }
}
"""
        response = self.graphql_request(request_string=query, context={"user": self.user})
        assert response is not None and "data" in response
        all_delivery_mechanisms = response["data"]["allDeliveryMechanisms"]
        assert all(key in entry for entry in all_delivery_mechanisms for key in ["name", "value"])

    def test_lacking_delivery_mechanisms(self):
        target_population = TargetPopulationFactory(
            created_by=self.user,
            candidate_list_targeting_criteria=(TargetingCriteriaFactory()),
            business_area=self.business_area,
            status=TargetPopulation.STATUS_LOCKED,
        )
        target_population.apply_criteria_query()  # simulate having TP households calculated
        payment_plan = PaymentPlanFactory(
            total_households_count=3, target_population=target_population, status=PaymentPlan.Status.LOCKED
        )

        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        choose_dms_mutation_variables_mutation_variables = dict(
            input=dict(
                paymentPlanId=encoded_payment_plan_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_CHEQUE],
            )
        )
        response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=choose_dms_mutation_variables_mutation_variables,
        )
        assert "errors" in response, response
        error_message = response["errors"][0]["message"]
        assert "Selected delivery mechanisms are not sufficient to serve all beneficiaries" in error_message
        assert "Delivery mechanisms that may be needed: " in error_message
        assert GenericPayment.DELIVERY_TYPE_TRANSFER in error_message
        assert GenericPayment.DELIVERY_TYPE_VOUCHER in error_message

    def test_providing_non_unique_delivery_mechanisms(self):
        payment_plan = PaymentPlanFactory(total_households_count=1, status=PaymentPlan.Status.LOCKED)
        encoded_payment_plan_id = encode_id_base64(payment_plan.id, "PaymentPlan")
        choose_dms_mutation_variables_mutation_variables = dict(
            input=dict(
                paymentPlanId=encoded_payment_plan_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_TRANSFER],
            )
        )
        response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=choose_dms_mutation_variables_mutation_variables,
        )
        assert "errors" not in response, response

        current_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context={"user": self.user},
            variables={"id": encoded_payment_plan_id},
        )
        assert "errors" not in current_payment_plan_response, current_payment_plan_response
        data = current_payment_plan_response["data"]["paymentPlan"]
        assert len(data["deliveryMechanisms"]) == 2
        assert data["deliveryMechanisms"][0]["name"] == GenericPayment.DELIVERY_TYPE_TRANSFER
        assert data["deliveryMechanisms"][1]["name"] == GenericPayment.DELIVERY_TYPE_TRANSFER


class TestFSPAssignment(APITestCase):
    @classmethod
    def setUpTestData(cls):
        base_setup(cls)
        payment_plan_setup(cls)

    def test_assigning_fsps_to_delivery_mechanism(self):
        choose_dms_mutation_variables_mutation_variables = dict(
            input=dict(
                paymentPlanId=self.encoded_payment_plan_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_VOUCHER],
            )
        )
        response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=choose_dms_mutation_variables_mutation_variables,
        )
        assert "errors" not in response, response

        available_mechanisms_query = """
query AvailableFspsForDeliveryMechanisms($deliveryMechanisms: [String!]!) {
    availableFspsForDeliveryMechanisms(deliveryMechanisms: $deliveryMechanisms) {
        deliveryMechanism
        fsps {
            id
            name
        }
    }
}
"""
        query_response = self.graphql_request(
            request_string=available_mechanisms_query,
            context={"user": self.user},
            variables={
                "deliveryMechanisms": [GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_VOUCHER]
            },
        )
        available_mechs_data = query_response["data"]["availableFspsForDeliveryMechanisms"]
        assert len(available_mechs_data) == 2
        assert available_mechs_data[0]["deliveryMechanism"] == GenericPayment.DELIVERY_TYPE_TRANSFER
        transfer_fsps_names = [x["name"] for x in available_mechs_data[0]["fsps"]]
        assert all(name in transfer_fsps_names for name in ["Santander", "Bank of Europe"])
        assert available_mechs_data[1]["deliveryMechanism"] == GenericPayment.DELIVERY_TYPE_VOUCHER
        voucher_fsp_names = [f["name"] for f in available_mechs_data[1]["fsps"]]
        assert "Bank of America" in voucher_fsp_names
        assert "Bank of Europe" in voucher_fsp_names

        bad_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    }
                ],
            },
        )
        assert "errors" in bad_mutation_response, bad_mutation_response
        assert (
            bad_mutation_response["errors"][0]["message"]
            == "Please assign FSP to all delivery mechanisms before moving to next step"
        )

        current_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context={"user": self.user},
            variables={"id": self.encoded_payment_plan_id},
        )
        data = current_payment_plan_response["data"]["paymentPlan"]
        assert len(data["deliveryMechanisms"]) == 2
        assert data["deliveryMechanisms"][0]["fsp"] is None
        assert data["deliveryMechanisms"][1]["fsp"] is None

        complete_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 2,
                    },
                ],
            },
        )
        assert "errors" not in complete_mutation_response, complete_mutation_response
        complete_payment_plan_data = complete_mutation_response["data"]["assignFspToDeliveryMechanism"]["paymentPlan"]
        assert complete_payment_plan_data["deliveryMechanisms"][0]["fsp"]["id"] == self.encoded_santander_fsp_id
        assert complete_payment_plan_data["deliveryMechanisms"][1]["fsp"]["id"] == self.encoded_bank_of_america_fsp_id

        new_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context={"user": self.user},
            variables={"id": self.encoded_payment_plan_id},
        )
        new_data = new_payment_plan_response["data"]["paymentPlan"]
        assert len(new_data["deliveryMechanisms"]) == 2
        assert new_data["deliveryMechanisms"][0]["fsp"]["id"] == self.encoded_santander_fsp_id
        assert new_data["deliveryMechanisms"][1]["fsp"]["id"] == self.encoded_bank_of_america_fsp_id

    def test_editing_fsps_assignments(self):
        choose_dms_mutation_variables = dict(
            input=dict(
                paymentPlanId=self.encoded_payment_plan_id,
                deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_VOUCHER],
            )
        )
        response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=choose_dms_mutation_variables,
        )
        assert "errors" not in response, response

        complete_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 2,
                    },
                ],
            },
        )
        assert "errors" not in complete_mutation_response, complete_mutation_response
        complete_payment_plan_data = complete_mutation_response["data"]["assignFspToDeliveryMechanism"]["paymentPlan"]
        assert complete_payment_plan_data["deliveryMechanisms"][0]["fsp"]["id"] == self.encoded_santander_fsp_id
        assert complete_payment_plan_data["deliveryMechanisms"][1]["fsp"]["id"] == self.encoded_bank_of_america_fsp_id

        payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context={"user": self.user},
            variables={"id": self.encoded_payment_plan_id},
        )
        new_data = payment_plan_response["data"]["paymentPlan"]
        assert len(new_data["deliveryMechanisms"]) == 2
        assert new_data["deliveryMechanisms"][0]["fsp"] is not None
        assert new_data["deliveryMechanisms"][1]["fsp"] is not None

        for fsp in [self.santander_fsp, self.bank_of_america_fsp, self.bank_of_europe_fsp]:
            fsp.delivery_mechanisms.append(GenericPayment.DELIVERY_TYPE_MOBILE_MONEY)

        for individual in [self.individuals_1[0], self.individuals_2[0], self.individuals_3[0]]:
            PaymentChannelFactory(
                individual=individual,
                delivery_mechanism=GenericPayment.DELIVERY_TYPE_MOBILE_MONEY,
            )

        new_program_mutation_variables = dict(
            input=dict(
                paymentPlanId=self.encoded_payment_plan_id,
                deliveryMechanisms=[
                    GenericPayment.DELIVERY_TYPE_MOBILE_MONEY,
                ],
            )
        )
        new_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=new_program_mutation_variables,
        )
        assert "errors" not in new_response

        edited_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context={"user": self.user},
            variables={"id": self.encoded_payment_plan_id},
        )
        edited_payment_plan_data = edited_payment_plan_response["data"]["paymentPlan"]
        assert len(edited_payment_plan_data["deliveryMechanisms"]) == 1

    def test_editing_fsps_assignments_when_fsp_was_already_set_up(self):
        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=self.encoded_payment_plan_id,
                    deliveryMechanisms=[GenericPayment.DELIVERY_TYPE_TRANSFER, GenericPayment.DELIVERY_TYPE_VOUCHER],
                )
            ),
        )
        assert "errors" not in choose_dms_response, choose_dms_response

        assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 2,
                    },
                ],
            },
        )
        assert "errors" not in assign_fsps_mutation_response, assign_fsps_mutation_response

        current_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context={"user": self.user},
            variables={"id": self.encoded_payment_plan_id},
        )
        current_data = current_payment_plan_response["data"]["paymentPlan"]
        assert len(current_data["deliveryMechanisms"]) == 2
        assert current_data["deliveryMechanisms"][0]["fsp"] is not None
        assert current_data["deliveryMechanisms"][1]["fsp"] is not None

        new_choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=self.encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_VOUCHER,
                        GenericPayment.DELIVERY_TYPE_TRANSFER,
                    ],  # different order
                )
            ),
        )
        assert "errors" not in new_choose_dms_response, new_choose_dms_response

        new_payment_plan_response = self.graphql_request(
            request_string=CURRENT_PAYMENT_PLAN_QUERY,
            context={"user": self.user},
            variables={"id": self.encoded_payment_plan_id},
        )
        new_data = new_payment_plan_response["data"]["paymentPlan"]
        assert len(new_data["deliveryMechanisms"]) == 2
        assert new_data["deliveryMechanisms"][0]["fsp"] is None
        assert new_data["deliveryMechanisms"][1]["fsp"] is None

    def test_choosing_different_fsps_for_the_same_delivery_mechanism(self):
        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=self.encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_TRANSFER,
                        GenericPayment.DELIVERY_TYPE_TRANSFER,
                        GenericPayment.DELIVERY_TYPE_VOUCHER,
                    ],
                )
            ),
        )
        assert "errors" not in choose_dms_response, choose_dms_response

        bad_assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_bank_of_america_fsp_id,  # doesn't support transfer
                        "order": 2,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 3,
                    },
                ],
            },
        )
        assert "errors" in bad_assign_fsps_mutation_response, bad_assign_fsps_mutation_response

        another_bad_assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,  # already chosen
                        "order": 2,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 3,
                    },
                ],
            },
        )
        assert "errors" in another_bad_assign_fsps_mutation_response, another_bad_assign_fsps_mutation_response
        assert (
            another_bad_assign_fsps_mutation_response["errors"][0]["message"]
            == "You can't assign the same FSP to the same delivery mechanism more than once"
        )

        assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_bank_of_europe_fsp_id,  # supports transfer
                        "order": 2,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,
                        "order": 3,
                    },
                ],
            },
        )
        assert "errors" not in assign_fsps_mutation_response, assign_fsps_mutation_response


class TestSpecialTreatmentWithCashDeliveryMechanism(APITestCase):
    @classmethod
    def setUpTestData(cls):
        base_setup(cls)

        cls.household_4, cls.individuals_4 = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
            },
            individuals_data=[{}],
        )

    def test_treating_collector_without_payment_channel_as_a_default_cash_option(self):
        IndividualRoleInHouseholdFactory(
            individual=self.individuals_4[0],
            household=self.household_4,
            role=ROLE_PRIMARY,
        )
        # no payment channels

        payment_plan_setup(self)

        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=self.encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_TRANSFER,
                        GenericPayment.DELIVERY_TYPE_VOUCHER,
                        # lacking cash option for ind #4
                    ],
                )
            ),
        )
        assert "errors" in choose_dms_response, choose_dms_response
        error_msg = choose_dms_response["errors"][0]["message"]
        assert GenericPayment.DELIVERY_TYPE_CASH in error_msg, error_msg

        choose_dms_with_cash_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=self.encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_TRANSFER,
                        GenericPayment.DELIVERY_TYPE_VOUCHER,
                        GenericPayment.DELIVERY_TYPE_CASH,
                    ],
                )
            ),
        )
        assert "errors" not in choose_dms_with_cash_response, choose_dms_with_cash_response

    def test_sufficient_delivery_mechanisms_for_collector_with_cash_payment_channel(self):
        IndividualRoleInHouseholdFactory(
            individual=self.individuals_4[0],
            household=self.household_4,
            role=ROLE_PRIMARY,
        )
        PaymentChannelFactory(
            individual=self.individuals_4[0],
            delivery_mechanism=GenericPayment.DELIVERY_TYPE_CASH,
        )

        payment_plan_setup(self)

        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=self.encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_TRANSFER,
                        GenericPayment.DELIVERY_TYPE_VOUCHER,
                        # lacking cash option for ind #4
                    ],
                )
            ),
        )
        assert "errors" in choose_dms_response, choose_dms_response
        error_msg = choose_dms_response["errors"][0]["message"]
        assert GenericPayment.DELIVERY_TYPE_CASH in error_msg, error_msg

        choose_dms_with_cash_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=self.encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_TRANSFER,
                        GenericPayment.DELIVERY_TYPE_VOUCHER,
                        GenericPayment.DELIVERY_TYPE_CASH,
                    ],
                )
            ),
        )
        assert "errors" not in choose_dms_with_cash_response, choose_dms_with_cash_response


class TestFSPLimit(APITestCase):
    @classmethod
    def setUpTestData(cls):
        base_setup(cls)
        payment_plan_setup(cls)

    def test_using_fsp_in_multiple_payment_plans_for_no_limnit(self):
        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=self.encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_TRANSFER,
                        GenericPayment.DELIVERY_TYPE_VOUCHER,
                    ],
                )
            ),
        )
        assert "errors" not in choose_dms_response, choose_dms_response

        assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,  # no limit
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,  # limit
                        "order": 2,
                    },
                ],
            },
        )
        assert "errors" not in assign_fsps_mutation_response, assign_fsps_mutation_response

        new_target_population = TargetPopulationFactory(
            created_by=self.user,
            candidate_list_targeting_criteria=(TargetingCriteriaFactory()),
            business_area=self.business_area,
            status=TargetPopulation.STATUS_LOCKED,
        )
        new_target_population.households.set([self.household_2])  # instead of applying criteria
        # household_2 supports transfer & cash
        new_payment_plan = PaymentPlanFactory(
            total_households_count=1, target_population=new_target_population, status=PaymentPlan.Status.LOCKED
        )

        new_encoded_payment_plan_id = encode_id_base64(new_payment_plan.id, "PaymentPlan")
        new_choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=new_encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_TRANSFER,
                    ],
                )
            ),
        )
        assert "errors" not in new_choose_dms_response, new_choose_dms_response

        new_assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": new_encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,  # no limit
                        "order": 1,
                    }
                ],
            },
        )
        assert "errors" not in new_assign_fsps_mutation_response, new_assign_fsps_mutation_response

    def test_using_fsp_in_multiple_payment_plans_while_having_a_limit(self):
        choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=self.encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_TRANSFER,
                        GenericPayment.DELIVERY_TYPE_VOUCHER,
                    ],
                )
            ),
        )
        assert "errors" not in choose_dms_response, choose_dms_response

        assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": self.encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_TRANSFER,
                        "fspId": self.encoded_santander_fsp_id,  # no limit
                        "order": 1,
                    },
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,  # limit
                        "order": 2,
                    },
                ],
            },
        )
        assert "errors" not in assign_fsps_mutation_response, assign_fsps_mutation_response

        new_target_population = TargetPopulationFactory(
            created_by=self.user,
            candidate_list_targeting_criteria=(TargetingCriteriaFactory()),
            business_area=self.business_area,
            status=TargetPopulation.STATUS_LOCKED,
        )
        new_target_population.households.set([self.household_1])  # instead of applying criteria
        # household_1 supports cash & voucher
        new_payment_plan = PaymentPlanFactory(
            total_households_count=1, target_population=new_target_population, status=PaymentPlan.Status.LOCKED
        )

        new_encoded_payment_plan_id = encode_id_base64(new_payment_plan.id, "PaymentPlan")
        new_choose_dms_response = self.graphql_request(
            request_string=CHOOSE_DELIVERY_MECHANISMS_MUTATION,
            context={"user": self.user},
            variables=dict(
                input=dict(
                    paymentPlanId=new_encoded_payment_plan_id,
                    deliveryMechanisms=[
                        GenericPayment.DELIVERY_TYPE_VOUCHER,
                    ],
                )
            ),
        )
        assert "errors" not in new_choose_dms_response, new_choose_dms_response

        # in query, america should not be visible for VOUCHER

        new_assign_fsps_mutation_response = self.graphql_request(
            request_string=ASSIGN_FSPS_MUTATION,
            context={"user": self.user},
            variables={
                "paymentPlanId": new_encoded_payment_plan_id,
                "mappings": [
                    {
                        "deliveryMechanism": GenericPayment.DELIVERY_TYPE_VOUCHER,
                        "fspId": self.encoded_bank_of_america_fsp_id,  # limit
                        "order": 1,
                    }
                ],
            },
        )
        # error because limit is exceeded
        assert "errors" not in new_assign_fsps_mutation_response, new_assign_fsps_mutation_response
