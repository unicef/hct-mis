from graphql import GraphQLError

from hct_mis_api.apps.payment.models import CashPlanPaymentVerification


class PaymentVerificationArgumentVerifier:
    ARGUMENTS = {
        "sampling": {
            CashPlanPaymentVerification.SAMPLING_FULL_LIST: {
                "required": ["full_list_arguments"],
                "not_allowed": ["random_sampling_arguments"],
            },
            CashPlanPaymentVerification.SAMPLING_RANDOM: {
                "required": ["random_sampling_arguments"],
                "not_allowed": ["full_list_arguments"],
            },
        },
        "verification_channel": {
            CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO: {
                "required": ["rapid_pro_arguments"],
                "not_allowed": ["xlsx_arguments", "manual_arguments"],
            },
            CashPlanPaymentVerification.VERIFICATION_METHOD_XLSX: {
                "required": [],
                "not_allowed": ["rapid_pro_arguments", "manual_arguments"],
            },
            CashPlanPaymentVerification.VERIFICATION_METHOD_MANUAL: {
                "required": [],
                "not_allowed": ["rapid_pro_arguments", "xlsx_arguments"],
            },
        },
    }

    def __init__(self, input):
        self.input = input

    def verify(self, field_name):
        options = self.ARGUMENTS.get(field_name)

        for key, value in options.items():
            if key != self.input.get(field_name):
                continue
            for required in value.get("required"):
                if self.input.get(required) is None:
                    raise GraphQLError(f"You have to provide {required} in {key}")
            for not_allowed in value.get("not_allowed"):
                if self.input.get(not_allowed) is not None:
                    raise GraphQLError(f"You can't provide {not_allowed} in {key}")
