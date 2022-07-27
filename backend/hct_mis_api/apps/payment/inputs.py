import graphene


class FullListArguments(graphene.InputObjectType):
    excluded_admin_areas = graphene.List(graphene.String)


class AgeInput(graphene.InputObjectType):
    min = graphene.Int()
    max = graphene.Int()


class RandomSamplingArguments(graphene.InputObjectType):
    confidence_interval = graphene.Float(required=True)
    margin_of_error = graphene.Float(required=True)
    excluded_admin_areas = graphene.List(graphene.String)
    age = AgeInput()
    sex = graphene.String()


class RapidProArguments(graphene.InputObjectType):
    flow_id = graphene.String(required=True)


class ManualArguments(graphene.InputObjectType):
    pass


class CreatePaymentVerificationInput(graphene.InputObjectType):
    cash_plan_id = graphene.ID(required=True)
    sampling = graphene.String(required=True)
    verification_channel = graphene.String(required=True)
    business_area_slug = graphene.String(required=True)
    full_list_arguments = FullListArguments()
    random_sampling_arguments = RandomSamplingArguments()
    rapid_pro_arguments = RapidProArguments()


class EditCashPlanPaymentVerificationInput(graphene.InputObjectType):
    cash_plan_payment_verification_id = graphene.ID(required=True)
    sampling = graphene.String(required=True)
    verification_channel = graphene.String(required=True)
    business_area_slug = graphene.String(required=True)
    full_list_arguments = FullListArguments()
    random_sampling_arguments = RandomSamplingArguments()
    rapid_pro_arguments = RapidProArguments()


class GetCashplanVerificationSampleSizeInput(graphene.InputObjectType):
    cash_plan_id = graphene.ID()
    cash_plan_payment_verification_id = graphene.ID()
    sampling = graphene.String(required=True)
    verification_channel = graphene.String()
    business_area_slug = graphene.String(required=True)
    full_list_arguments = FullListArguments()
    random_sampling_arguments = RandomSamplingArguments()
    rapid_pro_arguments = RapidProArguments()


class CreateFinancialServiceProviderInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    vision_vendor_number = graphene.String(required=True)
    delivery_mechanisms = graphene.List(graphene.String, required=True)
    distribution_limit = graphene.Decimal()
    communication_channel = graphene.String(required=True)
    fsp_xlsx_template_id = graphene.ID(required=True)


class PaymentPlanActionType(graphene.Enum):
    LOCK = "LOCK"
    UNLOCK = "UNLOCK"
    SEND_FOR_APPROVAL = "SEND_FOR_APPROVAL"
    APPROVE = "APPROVE"
    AUTHORIZE = "AUTHORIZE"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


class ActionPaymentPlanInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    action = graphene.InputField(PaymentPlanActionType, required=True)
    comment = graphene.String()


class CreatePaymentPlanInput(graphene.InputObjectType):
    business_area_slug = graphene.String(required=True)
    name = graphene.String(required=True)
    targeting_id = graphene.ID(required=True)
    start_date = graphene.Date(required=True)
    end_date = graphene.Date(required=True)
    dispersion_start_date = graphene.Date(required=True)
    dispersion_end_date = graphene.Date(required=True)
    currency = graphene.String(required=True)


class UpdatePaymentPlanInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    name = graphene.String(required=False)
    targeting_id = graphene.ID(required=False)
    start_date = graphene.Date(required=False)
    end_date = graphene.Date(required=False)
    dispersion_start_date = graphene.Date(required=False)
    dispersion_end_date = graphene.Date(required=False)
    currency = graphene.String(required=False)
