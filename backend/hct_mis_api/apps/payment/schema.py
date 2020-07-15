import graphene
from django.core.exceptions import ValidationError
from django.db import transaction
from django_filters import FilterSet, OrderingFilter
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_file_upload.scalars import Upload

from core.permissions import is_authenticated
from core.schema import ChoiceObject
from core.extended_connection import ExtendedConnection
from core.utils import to_choice_object
from payment.models import (
    PaymentRecord,
    ServiceProvider,
    CashPlanPaymentVerification,
    PaymentVerification,
)
from program.schema import CashPlanNode


class FullListArguments(graphene.InputObjectType):
    excluded_admin_areas = graphene.List(graphene.String)


class AgeInput(graphene.InputObjectType):
    min = graphene.Int()
    max = graphene.Int()


class RandomSamplingArguments(graphene.InputObjectType):
    confidence_interval = graphene.Int(required=True)
    margin_of_error = graphene.Int(required=True)
    excluded_admin_areas = graphene.List(graphene.String)
    age = AgeInput()
    sex = graphene.String()


class RapidProArguments(graphene.InputObjectType):
    flow_id = graphene.String(required=True)


class XlsxArguments(graphene.InputObjectType):
    file = Upload(required=True)


class ManualArguments(graphene.InputObjectType):
    pass


class CreatePaymentVerificationInput(graphene.InputObjectType):
    sampling = graphene.String(required=True)
    verification_channel = graphene.String(required=True)
    full_list_arguments = FullListArguments()
    random_sampling_arguments = RandomSamplingArguments()
    rapid_pro_arguments = RapidProArguments()
    xlsx_arguments = XlsxArguments()
    manual_arguments = ManualArguments


class CreatePaymentVerificationMutation(graphene.Mutation):

    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        input = CreatePaymentVerificationInput(required=True)

    @staticmethod
    def verify_required_arguments(input, field_name, options):
        for key, value in options:
            if key != input.get(field_name):
                continue
            for required in value.get("required"):
                if input.get(required) is None:
                    raise ValidationError(
                        f"You have to provide {required} in {key}"
                    )
            for not_allowed in value.get("not_allowed"):
                if input.get(not_allowed) is not None:
                    raise ValidationError(
                        f"You can't provide {not_allowed} in {key}"
                    )

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, input, **kwargs):
        arg = lambda name: input.get(name)
        cls.verify_required_arguments(
            input,
            "sampling",
            {
                CashPlanPaymentVerification.SAMPLING_FULL_LIST: {
                    "required": ["full_list_arguments"],
                    "not_allowed": ["random_sampling_arguments"],
                },
                CashPlanPaymentVerification.SAMPLING_RANDOM: {
                    "required": ["random_sampling_arguments"],
                    "not_allowed": ["full_list_arguments"],
                },
            },
        )
        cls.verify_required_arguments(
            input,
            "verification_channel",
            {
                CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO: {
                    "required": ["rapid_pro_arguments"],
                    "not_allowed": ["xlsx_arguments", "manual_arguments"],
                },
                CashPlanPaymentVerification.VERIFICATION_METHOD_XLSX: {
                    "required": ["xlsx_arguments"],
                    "not_allowed": ["rapid_pro_arguments", "manual_arguments"],
                },
                CashPlanPaymentVerification.VERIFICATION_METHOD_MANUAL: {
                    "required": ["manual_arguments"],
                    "not_allowed": ["rapid_pro_arguments", "xlsx_arguments"],
                },
            },
        )



class PaymentRecordFilter(FilterSet):
    class Meta:
        fields = (
            "cash_plan",
            "household",
        )
        model = PaymentRecord

    order_by = OrderingFilter(
        fields=(
            "status",
            "name",
            "status_date",
            "cash_assist_id",
            "head_of_household",
            "total_person_covered",
            "distribution_modality",
            "household__id",
            "entitlement__entitlement_quantity",
            "entitlement__delivered_quantity",
            "entitlement__delivery_date",
        )
    )


class PaymentRecordNode(DjangoObjectType):
    class Meta:
        model = PaymentRecord
        filter_fields = ["cash_plan", "household"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ServiceProviderNode(DjangoObjectType):
    class Meta:
        model = ServiceProvider
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class CashPlanPaymentVerificationNode(DjangoObjectType):
    class Meta:
        model = CashPlanPaymentVerification


class PaymentVerificationNode(DjangoObjectType):
    class Meta:
        model = PaymentVerification
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    payment_record = relay.Node.Field(PaymentRecordNode)
    all_payment_records = DjangoFilterConnectionField(
        PaymentRecordNode, filterset_class=PaymentRecordFilter,
    )
    payment_record_status_choices = graphene.List(ChoiceObject)
    payment_record_entitlement_card_status_choices = graphene.List(ChoiceObject)
    payment_record_delivery_type_choices = graphene.List(ChoiceObject)
    cash_plan_verification_status_choices = graphene.List(ChoiceObject)
    cash_plan_verification_sampling_choices = graphene.List(ChoiceObject)
    cash_plan_verification_verification_method_choices = graphene.List(
        ChoiceObject
    )
    payment_verification_status_choices = graphene.List(ChoiceObject)

    def resolve_payment_record_status_choices(self, info, **kwargs):
        return to_choice_object(PaymentRecord.STATUS_CHOICE)

    def resolve_payment_record_status_choices(self, info, **kwargs):
        return to_choice_object(PaymentRecord.ENTITLEMENT_CARD_STATUS_CHOICE)

    def resolve_payment_record_delivery_type_choices(self, info, **kwargs):
        return to_choice_object(PaymentRecord.DELIVERY_TYPE_CHOICE)

    def resolve_cash_plan_verification_status_choices(self, info, **kwargs):
        return to_choice_object(CashPlanPaymentVerification.STATUS_CHOICES)

    def resolve_cash_plan_verification_sampling_choices(self, info, **kwargs):
        return to_choice_object(CashPlanPaymentVerification.SAMPLING_CHOICES)

    def resolve_cash_plan_verification_verification_method_choices(
        self, info, **kwargs
    ):
        return to_choice_object(
            CashPlanPaymentVerification.VERIFICATION_METHOD_CHOICES
        )

    def resolve_payment_verification_status_choices(self, info, **kwargs):
        return to_choice_object(PaymentVerification.STATUS_CHOICES)
