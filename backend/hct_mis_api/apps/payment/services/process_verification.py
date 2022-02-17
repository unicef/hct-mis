from hct_mis_api.apps.payment.models import CashPlanPaymentVerification


class ProcessVerification:
    def __init__(self, input_data, cash_plan_payment_verification: CashPlanPaymentVerification):
        self.input_data = input_data
        self.cash_plan_payment_verification = cash_plan_payment_verification

    def process(self):
        verification_method = self.cash_plan_payment_verification.verification_method
        if verification_method == CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO:
            flow_id = self.input_data["rapid_pro_arguments"]["flow_id"]
            self.cash_plan_payment_verification.rapid_pro_flow_id = flow_id
            self.cash_plan_payment_verification.save()
