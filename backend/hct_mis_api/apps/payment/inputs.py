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


class UpdatePaymentPlanStatusInput(graphene.InputObjectType):
    payment_plan_id = graphene.ID(required=True)
    status = graphene.String()
    comment = graphene.String()
