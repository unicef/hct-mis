import math
from decimal import Decimal

import graphene
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from graphene_file_upload.scalars import Upload
from graphql import GraphQLError

from hct_mis_api.apps.account.permissions import PermissionMutation, Permissions
from hct_mis_api.apps.core.filters import filter_age
from hct_mis_api.apps.core.permissions import is_authenticated
from hct_mis_api.apps.core.utils import decode_id_string, check_concurrency_version_in_mutation
from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketPaymentVerificationDetails
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.payment.inputs import (
    CreatePaymentVerificationInput,
    EditCashPlanPaymentVerificationInput,
)
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification, PaymentVerification, PaymentRecord
from hct_mis_api.apps.payment.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.payment.schema import PaymentVerificationNode
from hct_mis_api.apps.payment.utils import get_number_of_samples, from_received_to_status, calculate_counts
from hct_mis_api.apps.payment.xlsx.XlsxVerificationImportService import XlsxVerificationImportService
from hct_mis_api.apps.program.models import CashPlan
from hct_mis_api.apps.program.schema import CashPlanNode

from hct_mis_api.core.scalars import BigInt


class CreatePaymentVerificationMutation(PermissionMutation):

    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        input = CreatePaymentVerificationInput(required=True)

    @staticmethod
    def verify_required_arguments(input, field_name, options):
        for key, value in options.items():
            if key != input.get(field_name):
                continue
            for required in value.get("required"):
                if input.get(required) is None:
                    raise GraphQLError(f"You have to provide {required} in {key}")
            for not_allowed in value.get("not_allowed"):
                if input.get(not_allowed) is not None:
                    raise GraphQLError(f"You can't provide {not_allowed} in {key}")

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
                    "required": [],
                    "not_allowed": ["rapid_pro_arguments", "manual_arguments"],
                },
                CashPlanPaymentVerification.VERIFICATION_METHOD_MANUAL: {
                    "required": [],
                    "not_allowed": ["rapid_pro_arguments", "xlsx_arguments"],
                },
            },
        )

        cash_plan_id = decode_id_string(arg("cash_plan_id"))
        cash_plan = get_object_or_404(CashPlan, id=cash_plan_id)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_CREATE, cash_plan.business_area)

        verification_channel = arg("verification_channel")
        if cash_plan.verifications.count() > 0:
            raise GraphQLError("Verification plan for this Cash Plan already exists")
        (
            payment_records,
            confidence_interval,
            margin_of_error,
            payment_records_sample_count,
            sampling,
            excluded_admin_areas,
            sex,
            age,
        ) = cls.process_sampling(cash_plan, input)
        cash_plan_verification = CashPlanPaymentVerification(
            cash_plan=cash_plan,
            confidence_interval=confidence_interval,
            margin_of_error=margin_of_error,
            sample_size=payment_records_sample_count,
            sampling=sampling,
            verification_method=verification_channel,
        )
        cash_plan_verification.sex_filter = sex
        cash_plan_verification.age_filter = age
        cash_plan_verification.excluded_admin_areas_filter = excluded_admin_areas
        payment_record_verifications_to_create = []
        for payment_record in payment_records:
            payment_record_verification = PaymentVerification(
                status_date=timezone.now(),
                cash_plan_payment_verification=cash_plan_verification,
                payment_record=payment_record,
            )
            payment_record_verifications_to_create.append(payment_record_verification)
        cash_plan_verification.save()
        PaymentVerification.objects.bulk_create(payment_record_verifications_to_create)
        cash_plan.refresh_from_db()
        cls.process_verification_method(cash_plan_verification, input)
        return cls(cash_plan=cash_plan)

    @classmethod
    def process_sampling(cls, cash_plan, input):
        arg = lambda name: input.get(name)
        sampling = arg("sampling")
        excluded_admin_areas = []
        sex = None
        age = None
        confidence_interval = None
        margin_of_error = None
        payment_records = cash_plan.payment_records.filter(
            status=PaymentRecord.STATUS_SUCCESS, delivered_quantity__gt=0
        )
        if sampling == CashPlanPaymentVerification.SAMPLING_FULL_LIST:
            excluded_admin_areas = arg("full_list_arguments").get("excluded_admin_areas", [])
        elif sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            random_sampling_arguments = arg("random_sampling_arguments")
            confidence_interval = random_sampling_arguments.get("confidence_interval")
            margin_of_error = random_sampling_arguments.get("margin_of_error")
            sex = random_sampling_arguments.get("sex")
            age = random_sampling_arguments.get("age")
            excluded_admin_areas = random_sampling_arguments.get("excluded_admin_areas", [])
        excluded_admin_areas_decoded = [decode_id_string(x) for x in excluded_admin_areas]

        payment_records = payment_records.filter(~(Q(household__admin_area__id__in=excluded_admin_areas_decoded)))
        if sex is not None:
            payment_records = payment_records.filter(household__head_of_household__sex=sex)
        if age is not None:
            payment_records = filter_age(
                "household__head_of_household__birth_date",
                payment_records,
                age.get("min"),
                age.get("max"),
            )
        payment_records_sample_count = payment_records.count()
        if sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            payment_records_sample_count = get_number_of_samples(
                payment_records_sample_count,
                confidence_interval,
                margin_of_error,
            )
            payment_records = payment_records.order_by("?")[:payment_records_sample_count]
        return (
            payment_records,
            confidence_interval,
            margin_of_error,
            payment_records_sample_count,
            sampling,
            excluded_admin_areas,
            sex,
            age,
        )

    @classmethod
    def process_verification_method(cls, cash_plan_payment_verification, input):
        verification_method = cash_plan_payment_verification.verification_method
        if verification_method == CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO:
            cls.process_rapid_pro_method(cash_plan_payment_verification, input)

    @classmethod
    def process_rapid_pro_method(cls, cash_plan_payment_verification, input):
        rapid_pro_arguments = input["rapid_pro_arguments"]
        flow_id = rapid_pro_arguments["flow_id"]
        cash_plan_payment_verification.rapid_pro_flow_id = flow_id

        cash_plan_payment_verification.save()


class EditPaymentVerificationMutation(PermissionMutation):

    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        input = EditCashPlanPaymentVerificationInput(required=True)
        version = BigInt(required=False)

    @staticmethod
    def verify_required_arguments(input, field_name, options):
        for key, value in options.items():
            if key != input.get(field_name):
                continue
            for required in value.get("required"):
                if input.get(required) is None:
                    raise GraphQLError(f"You have to provide {required} in {key}")
            for not_allowed in value.get("not_allowed"):
                if input.get(not_allowed) is not None:
                    raise GraphQLError(f"You can't provide {not_allowed} in {key}")

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
                    "required": [],
                    "not_allowed": ["rapid_pro_arguments", "manual_arguments"],
                },
                CashPlanPaymentVerification.VERIFICATION_METHOD_MANUAL: {
                    "required": [],
                    "not_allowed": ["rapid_pro_arguments", "xlsx_arguments"],
                },
            },
        )
        cash_plan_payment_verification_id = decode_id_string(arg("cash_plan_payment_verification_id"))

        cash_plan_verification = get_object_or_404(CashPlanPaymentVerification, id=cash_plan_payment_verification_id)
        check_concurrency_version_in_mutation(kwargs.get("version"), cash_plan_verification)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_UPDATE, cash_plan_verification.business_area)

        if cash_plan_verification.status != CashPlanPaymentVerification.STATUS_PENDING:
            raise GraphQLError("You can only edit PENDING Cash Plan Verification")
        cash_plan = cash_plan_verification.cash_plan
        verification_channel = arg("verification_channel")
        (
            payment_records,
            confidence_interval,
            margin_of_error,
            payment_records_sample_count,
            sampling,
            excluded_admin_areas,
            sex,
            age,
        ) = cls.process_sampling(cash_plan, input)

        cash_plan_verification.confidence_interval = confidence_interval
        cash_plan_verification.margin_of_error = margin_of_error
        cash_plan_verification.sample_size = payment_records_sample_count
        cash_plan_verification.sampling = sampling
        cash_plan_verification.verification_method = verification_channel
        cash_plan_verification.sex_filter = sex
        cash_plan_verification.age_filter = age
        cash_plan_verification.excluded_admin_areas_filter = excluded_admin_areas
        cash_plan_verification.payment_record_verifications.all().delete()
        payment_record_verifications_to_create = []
        for payment_record in payment_records:
            payment_record_verification = PaymentVerification(
                status_date=timezone.now(),
                cash_plan_payment_verification=cash_plan_verification,
                payment_record=payment_record,
            )
            payment_record_verifications_to_create.append(payment_record_verification)
        cash_plan_verification.save()
        PaymentVerification.objects.bulk_create(payment_record_verifications_to_create)
        cash_plan.refresh_from_db()
        cls.process_verification_method(cash_plan_verification, input)
        return cls(cash_plan=cash_plan)

    @classmethod
    def process_sampling(cls, cash_plan, input):
        arg = lambda name: input.get(name)
        sampling = arg("sampling")
        excluded_admin_areas = []
        sex = None
        age = None
        confidence_interval = None
        margin_of_error = None
        payment_records = cash_plan.payment_records.filter(
            status=PaymentRecord.STATUS_SUCCESS, delivered_quantity__gt=0
        )
        if sampling == CashPlanPaymentVerification.SAMPLING_FULL_LIST:
            excluded_admin_areas = arg("full_list_arguments").get("excluded_admin_areas", [])
        elif sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            random_sampling_arguments = arg("random_sampling_arguments")
            confidence_interval = random_sampling_arguments.get("confidence_interval")
            margin_of_error = random_sampling_arguments.get("margin_of_error")
            excluded_admin_areas = random_sampling_arguments.get("excluded_admin_areas", [])
            sex = random_sampling_arguments.get("sex")
            age = random_sampling_arguments.get("age")

        excluded_admin_areas_decoded = [decode_id_string(x) for x in excluded_admin_areas]

        payment_records = payment_records.filter(~(Q(household__admin_area__id__in=excluded_admin_areas_decoded)))
        if sex is not None:
            payment_records = payment_records.filter(household__head_of_household__sex=sex)
        if age is not None:
            payment_records = filter_age(
                "household__head_of_household__birth_date",
                payment_records,
                age.get("min"),
                age.get("max"),
            )
        payment_records_sample_count = payment_records.count()
        if sampling == CashPlanPaymentVerification.SAMPLING_RANDOM:
            payment_records_sample_count = get_number_of_samples(
                payment_records_sample_count,
                confidence_interval,
                margin_of_error,
            )
            payment_records = payment_records.order_by("?")[:payment_records_sample_count]
        return (
            payment_records,
            confidence_interval,
            margin_of_error,
            payment_records_sample_count,
            sampling,
            excluded_admin_areas,
            sex,
            age,
        )

    @classmethod
    def process_verification_method(cls, cash_plan_payment_verification, input):
        verification_method = cash_plan_payment_verification.verification_method
        if verification_method == CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO:
            cls.process_rapid_pro_method(cash_plan_payment_verification, input)

    @classmethod
    def process_rapid_pro_method(cls, cash_plan_payment_verification, input):
        rapid_pro_arguments = input["rapid_pro_arguments"]
        flow_id = rapid_pro_arguments["flow_id"]
        cash_plan_payment_verification.rapid_pro_flow_id = flow_id

        cash_plan_payment_verification.save()


class ActivateCashPlanVerificationMutation(PermissionMutation):

    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_verification_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, cash_plan_verification_id, **kwargs):
        id = decode_id_string(cash_plan_verification_id)
        cashplan_payment_verification = get_object_or_404(CashPlanPaymentVerification, id=id)
        check_concurrency_version_in_mutation(kwargs.get("version"), cashplan_payment_verification)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_ACTIVATE, cashplan_payment_verification.business_area)

        if cashplan_payment_verification.status != CashPlanPaymentVerification.STATUS_PENDING:
            raise GraphQLError("You can activate only PENDING verification")
        cashplan_payment_verification.status = CashPlanPaymentVerification.STATUS_ACTIVE
        if (
            cashplan_payment_verification.verification_method
            == CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO
        ):
            cls.activate_rapidpro(cashplan_payment_verification)
        cashplan_payment_verification.activation_date = timezone.now()
        cashplan_payment_verification.save()
        return ActivateCashPlanVerificationMutation(cashplan_payment_verification.cash_plan)

    @classmethod
    def activate_rapidpro(cls, cashplan_payment_verification):
        business_area_slug = cashplan_payment_verification.business_area.slug
        api = RapidProAPI(business_area_slug)
        phone_numbers = list(
            Individual.objects.filter(
                heading_household__payment_records__verifications__cash_plan_payment_verification=cashplan_payment_verification.id
            ).values_list("phone_no", flat=True)
        )
        # TODO Uncomment when correct phone numbers in user
        flow_start_info = api.start_flow(cashplan_payment_verification.rapid_pro_flow_id, phone_numbers)
        cashplan_payment_verification.rapid_pro_flow_start_uuid = flow_start_info.get("uuid")


class FinishCashPlanVerificationMutation(PermissionMutation):

    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_verification_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    def create_grievance_ticket_for_status(cls, cashplan_payment_verification, status):
        verifications = cashplan_payment_verification.payment_record_verifications.filter(status=status)
        if verifications.count() == 0:
            return
        grievance_ticket = GrievanceTicket.objects.create(
            category=GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION,
            business_area=cashplan_payment_verification.cash_plan.business_area,
        )
        details = TicketPaymentVerificationDetails(
            ticket=grievance_ticket,
            payment_verification_status=status,
        )
        details.payment_verifications.set(verifications)
        details.save()

    @classmethod
    def create_grievance_tickets(cls, cashplan_payment_verification):
        cls.create_grievance_ticket_for_status(cashplan_payment_verification, PaymentVerification.STATUS_PENDING)
        cls.create_grievance_ticket_for_status(cashplan_payment_verification, PaymentVerification.STATUS_NOT_RECEIVED)
        cls.create_grievance_ticket_for_status(
            cashplan_payment_verification, PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
        )

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, cash_plan_verification_id, **kwargs):
        id = decode_id_string(cash_plan_verification_id)
        cashplan_payment_verification = get_object_or_404(CashPlanPaymentVerification, id=id)
        check_concurrency_version_in_mutation(kwargs.get("version"), cashplan_payment_verification)
        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_FINISH, cashplan_payment_verification.business_area)

        if cashplan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            raise GraphQLError("You can finish only ACTIVE verification")
        cashplan_payment_verification.status = CashPlanPaymentVerification.STATUS_FINISHED
        cashplan_payment_verification.completion_date = timezone.now()
        cashplan_payment_verification.save()
        cls.create_grievance_tickets(cashplan_payment_verification)
        return ActivateCashPlanVerificationMutation(cashplan_payment_verification.cash_plan)


class DiscardCashPlanVerificationMutation(PermissionMutation):

    cash_plan = graphene.Field(CashPlanNode)

    class Arguments:
        cash_plan_verification_id = graphene.ID(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(cls, root, info, cash_plan_verification_id, **kwargs):
        id = decode_id_string(cash_plan_verification_id)
        cashplan_payment_verification = get_object_or_404(CashPlanPaymentVerification, id=id)
        check_concurrency_version_in_mutation(kwargs.get("version"), cashplan_payment_verification)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_DISCARD, cashplan_payment_verification.business_area)

        if cashplan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            raise GraphQLError("You can discard only ACTIVE verification")
        cash_plan = cashplan_payment_verification.cash_plan
        payment_records = cls.get_new_payment_records(cashplan_payment_verification)
        payment_record_verifications_to_create = []
        for payment_record in payment_records:
            payment_record_verification = PaymentVerification(
                status_date=timezone.now(),
                cash_plan_payment_verification=cashplan_payment_verification,
                payment_record=payment_record,
            )
            payment_record_verifications_to_create.append(payment_record_verification)
        cashplan_payment_verification.status = CashPlanPaymentVerification.STATUS_PENDING
        cash_plan.verification_status = CashPlanPaymentVerification.STATUS_PENDING
        cash_plan.save()
        cashplan_payment_verification.save()
        return DiscardCashPlanVerificationMutation(cash_plan)

    @classmethod
    def get_new_payment_records(cls, cash_plan_verification):
        payment_records = cash_plan_verification.cash_plan.payment_records.all()
        excluded_admin_areas = cash_plan_verification.excluded_admin_areas_filter
        sex = cash_plan_verification.sex_filter
        age = cash_plan_verification.age_filter
        if excluded_admin_areas:
            excluded_admin_areas_decoded = [decode_id_string(x) for x in excluded_admin_areas]
            payment_records = payment_records.filter(~(Q(household__admin_area__id__in=excluded_admin_areas_decoded)))
        if sex is not None:
            payment_records = payment_records.filter(household__head_of_household__sex=sex)
        if age is not None:
            payment_records = filter_age(
                "household__head_of_household__birth_date",
                payment_records,
                age.get("min"),
                age.get("max"),
            )
        return payment_records


class UpdatePaymentVerificationStatusAndReceivedAmount(graphene.Mutation):
    # TODO I don't think this is being used now, add permission if in use

    payment_verification = graphene.Field(PaymentVerificationNode)

    class Arguments:
        payment_verification_id = graphene.ID(required=True)
        received_amount = graphene.Decimal(required=True)
        status = graphene.Argument(
            graphene.Enum(
                "PaymentVerificationStatusForUpdate",
                [(x[0], x[0]) for x in PaymentVerification.STATUS_CHOICES],
            )
        )
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root,
        info,
        payment_verification_id,
        received_amount,
        status,
        **kwargs,
    ):
        payment_verification = get_object_or_404(PaymentVerification, id=decode_id_string(payment_verification_id))
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification)
        if (
            payment_verification.cash_plan_payment_verification.verification_method
            != CashPlanPaymentVerification.VERIFICATION_METHOD_MANUAL
        ):
            raise GraphQLError(f"You can only update status of payment verification for MANUAL verification method")
        if payment_verification.cash_plan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            raise GraphQLError(
                f"You can only update status of payment verification for {CashPlanPaymentVerification.STATUS_ACTIVE} cash plan verification"
            )
        delivered_amount = payment_verification.payment_record.delivered_quantity
        if status == PaymentVerification.STATUS_PENDING and received_amount is not None:
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_PENDING} when received_amount ({received_amount}) is not empty",
            )
        elif (
            status == PaymentVerification.STATUS_NOT_RECEIVED
            and received_amount is not None
            and received_amount != Decimal(0)
        ):
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_NOT_RECEIVED} when received_amount ({received_amount}) is not 0 or empty",
            )
        elif status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES and (
            received_amount is None or received_amount == Decimal(0)
        ):
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_RECEIVED_WITH_ISSUES} when received_amount ({received_amount}) is 0 or empty",
            )
        elif status == PaymentVerification.STATUS_RECEIVED and received_amount != delivered_amount:
            received_amount_text = "None" if received_amount is None else received_amount
            raise GraphQLError(
                f"Wrong status {PaymentVerification.STATUS_RECEIVED} when received_amount ({received_amount_text}) ≠ delivered_amount ({delivered_amount})"
            )
        payment_verification.status = status
        payment_verification.received_amount = received_amount
        payment_verification.save()
        cashplan_payment_verification = payment_verification.cash_plan_payment_verification
        calculate_counts(cashplan_payment_verification)
        cashplan_payment_verification.save()
        return UpdatePaymentVerificationStatusAndReceivedAmount(payment_verification)


class UpdatePaymentVerificationReceivedAndReceivedAmount(PermissionMutation):

    payment_verification = graphene.Field(PaymentVerificationNode)

    class Arguments:
        payment_verification_id = graphene.ID(required=True)
        received_amount = graphene.Decimal(required=True)
        received = graphene.Boolean(required=True)
        version = BigInt(required=False)

    @classmethod
    @is_authenticated
    @transaction.atomic
    def mutate(
        cls,
        root,
        info,
        payment_verification_id,
        received_amount,
        received,
        **kwargs,
    ):
        if math.isnan(received_amount):
            received_amount = None
        payment_verification = get_object_or_404(PaymentVerification, id=decode_id_string(payment_verification_id))
        check_concurrency_version_in_mutation(kwargs.get("version"), payment_verification)
        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_VERIFY, payment_verification.business_area)
        if (
            payment_verification.cash_plan_payment_verification.verification_method
            != CashPlanPaymentVerification.VERIFICATION_METHOD_MANUAL
        ):
            raise GraphQLError(f"You can only update status of payment verification for MANUAL verification method")
        if payment_verification.cash_plan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            raise GraphQLError(
                f"You can only update status of payment verification for {CashPlanPaymentVerification.STATUS_ACTIVE} cash plan verification"
            )
        delivered_amount = payment_verification.payment_record.delivered_quantity

        if received is None and received_amount is not None and received_amount == 0:
            raise GraphQLError(f"You can't set received_amount {received_amount} and not set received to NO")
        if received is None and received_amount is not None:
            raise GraphQLError(f"You can't set received_amount {received_amount} and not set received to YES")
        elif received_amount == 0 and received:
            raise GraphQLError(
                f"If received_amount is 0, you should set received to NO",
            )
        elif received_amount is not None and received_amount != 0 and not received:
            raise GraphQLError(f"If received_amount({received_amount}) is not 0, you should set received to YES")

        payment_verification.status = from_received_to_status(received, received_amount, delivered_amount)
        payment_verification.received_amount = received_amount
        payment_verification.save()
        cashplan_payment_verification = payment_verification.cash_plan_payment_verification
        calculate_counts(cashplan_payment_verification)
        cashplan_payment_verification.save()
        return UpdatePaymentVerificationStatusAndReceivedAmount(payment_verification)


class XlsxErrorNode(graphene.ObjectType):
    sheet = graphene.String()
    coordinates = graphene.String()
    message = graphene.String()

    def resolve_sheet(parent, info):
        return parent[0]

    def resolve_coordinates(parent, info):
        return parent[1]

    def resolve_message(parent, info):
        return parent[2]


class ImportXlsxCashPlanVerification(PermissionMutation):
    cash_plan = graphene.Field(CashPlanNode)
    errors = graphene.List(XlsxErrorNode)

    class Arguments:
        file = Upload(required=True)
        cash_plan_verification_id = graphene.ID(required=True)

    @classmethod
    @is_authenticated
    def mutate(cls, root, info, file, cash_plan_verification_id):
        id = decode_id_string(cash_plan_verification_id)
        cashplan_payment_verification = get_object_or_404(CashPlanPaymentVerification, id=id)

        cls.has_permission(info, Permissions.PAYMENT_VERIFICATION_IMPORT, cashplan_payment_verification.business_area)

        if cashplan_payment_verification.status != CashPlanPaymentVerification.STATUS_ACTIVE:
            raise GraphQLError("You can only import verification for active CashPlan verification")
        if cashplan_payment_verification.verification_method != CashPlanPaymentVerification.VERIFICATION_METHOD_XLSX:
            raise GraphQLError("You can only import verification when XLSX channel is selected")
        import_service = XlsxVerificationImportService(cashplan_payment_verification, file)
        import_service.open_workbook()
        import_service.validate()
        if len(import_service.errors):
            return ImportXlsxCashPlanVerification(None, import_service.errors)
        import_service.import_verifications()
        calculate_counts(cashplan_payment_verification)
        cashplan_payment_verification.save()
        return ImportXlsxCashPlanVerification(cashplan_payment_verification.cash_plan, import_service.errors)


class Mutations(graphene.ObjectType):
    create_cash_plan_payment_verification = CreatePaymentVerificationMutation.Field()
    edit_cash_plan_payment_verification = EditPaymentVerificationMutation.Field()
    import_xlsx_cash_plan_verification = ImportXlsxCashPlanVerification.Field()
    activate_cash_plan_payment_verification = ActivateCashPlanVerificationMutation.Field()
    finish_cash_plan_payment_verification = FinishCashPlanVerificationMutation.Field()
    discard_cash_plan_payment_verification = DiscardCashPlanVerificationMutation.Field()
    update_payment_verification_status_and_received_amount = UpdatePaymentVerificationStatusAndReceivedAmount.Field()
    update_payment_verification_received_and_received_amount = (
        UpdatePaymentVerificationReceivedAndReceivedAmount.Field()
    )
