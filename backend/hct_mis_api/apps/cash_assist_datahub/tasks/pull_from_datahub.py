import logging
import sys

from django.db import transaction
from django.db.models import Count
from django.utils.functional import cached_property

from sentry_sdk import configure_scope

from hct_mis_api.apps.cash_assist_datahub import models as ca_models
from hct_mis_api.apps.cash_assist_datahub.models import Session
from hct_mis_api.apps.core.exchange_rates import ExchangeRates
from hct_mis_api.apps.core.models import BusinessArea, CountryCodeMap
from hct_mis_api.apps.core.utils import nested_getattr
from hct_mis_api.apps.erp_datahub.utils import (
    get_exchange_rate_for_cash_plan,
    get_payment_record_delivered_quantity_in_usd,
)
from hct_mis_api.apps.payment.models import PaymentRecord, ServiceProvider
from hct_mis_api.apps.program.models import CashPlan, Program
from hct_mis_api.apps.targeting.models import TargetPopulation

logger = logging.getLogger(__name__)


class PullFromDatahubTask:
    MAPPING_CASH_PLAN_DICT = {
        "ca_id": "cash_plan_id",
        "ca_hash_id": "cash_plan_hash_id",
        "status": "status",
        "total_undelivered_quantity": "total_undelivered_quantity",
        "total_delivered_quantity": "total_delivered_quantity",
        "total_entitled_quantity_revised": "total_entitled_quantity_revised",
        "total_entitled_quantity": "total_entitled_quantity",
        "total_persons_covered_revised": "total_persons_covered_revised",
        "total_persons_covered": "total_persons_covered",
        "validation_alerts_count": "validation_alerts_count",
        "down_payment": "down_payment",
        "funds_commitment": "funds_commitment",
        "vision_id": "vision_id",
        "assistance_through": "assistance_through",
        "assistance_measurement": "assistance_measurement",
        "delivery_type": "delivery_type",
        "comments": "comments",
        "coverage_duration": "coverage_duration",
        "coverage_unit": "coverage_unit",
        "dispersion_date": "dispersion_date",
        "end_date": "end_date",
        "start_date": "start_date",
        "distribution_level": "distribution_level",
        "name": "name",
        "status_date": "status_date",
        "program_id": "program_mis_id",
    }
    MAPPING_PAYMENT_RECORD_DICT = {
        "delivery_date": "delivery_date",
        "delivered_quantity": "delivered_quantity",
        "entitlement_quantity": "entitlement_quantity",
        "currency": "currency",
        "delivery_type": "delivery_type",
        "entitlement_card_issue_date": "entitlement_card_issue_date",
        "entitlement_card_status": "entitlement_card_status",
        "entitlement_card_number": "entitlement_card_number",
        "target_population_id": "target_population_mis_id",
        "distribution_modality": "distribution_modality",
        "total_persons_covered": "total_persons_covered",
        "full_name": "full_name",
        "household_id": "household_mis_id",
        "head_of_household_id": "head_of_household_mis_id",
        "ca_id": "ca_id",
        "ca_hash_id": "ca_hash_id",
        "status": "status",
        "status_date": "status_date",
        "transaction_reference_id": "transaction_reference_id",
        "vision_id": "vision_id",
        "registration_ca_id": "registration_ca_id",
    }
    MAPPING_SERVICE_PROVIDER_DICT = {
        "ca_id": "ca_id",
        "full_name": "full_name",
        "short_name": "short_name",
        "vision_id": "vision_id",
    }

    def execute(self):
        grouped_session = Session.objects.values("business_area").annotate(count=Count("business_area"))
        ret = {
            "grouped_session": 0,
            "skipped_due_failure": [],
            "successes": [],
            "failures": [],
        }
        for group in grouped_session:
            ret["grouped_session"] += 1
            business_area = group.get("business_area")
            session_queryset = Session.objects.filter(business_area=business_area)
            # if any session in this business area fails omit other sessions in this business area
            if session_queryset.filter(status=Session.STATUS_FAILED).count() > 0:
                ret["skipped_due_failure"].append(business_area)
                continue
            sessions = session_queryset.filter(status=Session.STATUS_READY).order_by("-last_modified_date")
            for session in sessions:
                try:
                    self.copy_session(session)
                    ret["successes"].append(session.id)
                except Exception as e:
                    ret["failures"].append(session.id)
        return ret

    def build_arg_dict(self, model_object, mapping_dict):
        return {key: nested_getattr(model_object, mapping_dict[key]) for key in mapping_dict}

    def copy_session(self, session):
        with configure_scope() as scope:
            scope.set_tag("session.ca", str(session.id))
            STATUS = session.STATUS_PROCESSING
            TB = ""
            SID = ""
            session.status = STATUS
            session.save()
            try:
                with transaction.atomic(using="default"):
                    with transaction.atomic(using="cash_assist_datahub_ca"):
                        try:
                            self.copy_service_providers(session)
                            programs = self.copy_programs_ids(session)
                            Program.objects.bulk_update(programs, ["ca_id", "ca_hash_id"])
                            TargetPopulation.objects.bulk_update(
                                self.copy_target_population_ids(session), ["ca_id", "ca_hash_id"]
                            )
                            self.copy_cash_plans(session)
                            self.copy_payment_records(session)
                            STATUS = session.STATUS_COMPLETED
                        except Exception as e:
                            logger.exception(e)
                            session.process_exception(e)
                            STATUS = session.status
                            TB = session.traceback
                            SID = session.sentry_id
                            raise
            finally:
                session.sentry_id = SID
                session.traceback = TB
                session.status = STATUS
                session.save()

    def copy_cash_plans(self, session):
        dh_cash_plans = ca_models.CashPlan.objects.filter(session=session)
        for dh_cash_plan in dh_cash_plans:
            cash_plan_args = self.build_arg_dict(dh_cash_plan, PullFromDatahubTask.MAPPING_CASH_PLAN_DICT)
            self.set_cash_plan_service_provider(cash_plan_args)
            cash_plan_args["business_area"] = BusinessArea.objects.get(code=dh_cash_plan.business_area)
            (
                cash_plan,
                created,
            ) = CashPlan.objects.update_or_create(ca_id=dh_cash_plan.cash_plan_id, defaults=cash_plan_args)
            try:
                if not cash_plan.exchange_rate:
                    exchange_rates_client = ExchangeRates()
                    cash_plan.exchange_rate = get_exchange_rate_for_cash_plan(cash_plan, exchange_rates_client)
                    cash_plan.save(update_fields=["exchange_rate"])
            except Exception as e:
                logger.exception(e)

    def set_cash_plan_service_provider(self, cash_plan_args):
        assistance_through = cash_plan_args.get("assistance_through")
        if not assistance_through:
            return
        service_provider = ServiceProvider.objects.filter(ca_id=assistance_through).first()
        if service_provider is None:
            return
        cash_plan_args["service_provider"] = service_provider

    @cached_property
    def exchange_rates_client(self):
        return ExchangeRates()

    def copy_payment_records(self, session):
        dh_payment_records = ca_models.PaymentRecord.objects.filter(session=session)

        for dh_payment_record in dh_payment_records:
            payment_record_args = self.build_arg_dict(
                dh_payment_record,
                PullFromDatahubTask.MAPPING_PAYMENT_RECORD_DICT,
            )

            payment_record_args["business_area"] = BusinessArea.objects.get(code=dh_payment_record.business_area)
            payment_record_args["service_provider"] = ServiceProvider.objects.get(
                ca_id=dh_payment_record.service_provider_ca_id
            )
            payment_record_args["cash_plan"] = CashPlan.objects.get(ca_id=dh_payment_record.cash_plan_ca_id)
            (
                payment_record,
                created,
            ) = PaymentRecord.objects.update_or_create(ca_id=dh_payment_record.ca_id, defaults=payment_record_args)
            if not payment_record.delivered_quantity_usd:
                try:
                    payment_record.delivered_quantity_usd = get_payment_record_delivered_quantity_in_usd(
                        payment_record, self.exchange_rates_client
                    )
                except Exception as e:
                    logger.exception(e)
                payment_record.save(update_fields=["delivered_quantity_usd"])
            if payment_record.household and payment_record.cash_plan and payment_record.cash_plan.program:
                payment_record.household.programs.add(payment_record.cash_plan.program)

    def copy_service_providers(self, session):
        dh_service_providers = ca_models.ServiceProvider.objects.filter(session=session)
        for dh_service_provider in dh_service_providers:
            service_provider_args = self.build_arg_dict(
                dh_service_provider,
                PullFromDatahubTask.MAPPING_SERVICE_PROVIDER_DICT,
            )
            service_provider_args["business_area"] = BusinessArea.objects.get(code=dh_service_provider.business_area)
            service_provider_args["country"] = CountryCodeMap.objects.get_iso3_code(dh_service_provider.country)
            ServiceProvider.objects.update_or_create(ca_id=dh_service_provider.ca_id, defaults=service_provider_args)

    def copy_programs_ids(self, session):
        dh_programs = ca_models.Programme.objects.filter(session=session)
        programs = []
        for dh_program in dh_programs:
            program = Program.objects.get(id=dh_program.mis_id)
            program.ca_id = dh_program.ca_id
            program.ca_hash_id = dh_program.ca_hash_id
            programs.append(program)
        return programs

    def copy_target_population_ids(self, session):
        dh_target_populations = ca_models.TargetPopulation.objects.filter(session=session)

        for dh_target_population in dh_target_populations:
            target_population = TargetPopulation.objects.get(id=dh_target_population.mis_id)
            target_population.ca_id = dh_target_population.ca_id
            target_population.ca_hash_id = dh_target_population.ca_hash_id
            yield target_population
