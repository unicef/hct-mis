import multiprocessing
import time
from itertools import repeat

from django.core.management import BaseCommand

from core.fixtures import LocationFactory
from core.models import BusinessArea
from household.fixtures import (
    EntitlementCardFactory,
    HouseholdFactory,
    IndividualFactory,
)
from payment.fixtures import PaymentRecordFactory
from program.fixtures import CashPlanFactory, ProgramFactory
from targeting.fixtures import TargetPopulationFactory


class Command(BaseCommand):
    help = "Generate fixtures data for project"

    def add_arguments(self, parser):
        parser.add_argument(
            "--program",
            dest="programs_amount",
            const=10,
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of program objects.",
        )

        parser.add_argument(
            "--cash-plan",
            dest="cash_plans_amount",
            const=10,
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of cash plans for one program.",
        )

        parser.add_argument(
            "--payment-record",
            dest="payment_record_amount",
            const=10,
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of payment records assigned to "
            "household and cash plan.",
        )

    @staticmethod
    def _generate_program_with_dependencies(options):
        cash_plans_amount = options["cash_plans_amount"]
        payment_record_amount = options["payment_record_amount"]
        business_area = BusinessArea.objects.first()

        program = ProgramFactory.create(business_area=business_area)

        for _ in range(cash_plans_amount):
            cash_plan = CashPlanFactory.create(program=program)
            for _ in range(payment_record_amount):
                location = LocationFactory.create(business_area=business_area)
                household = HouseholdFactory.create(location=location)
                individuals = IndividualFactory.create_batch(
                    4, household=household,
                )
                household = HouseholdFactory.create(location=location)
                PaymentRecordFactory.create(
                    cash_plan=cash_plan, household=household
                )
                EntitlementCardFactory.create(household=household)
                TargetPopulationFactory.create(households=household)

    def handle(self, *args, **options):
        start_time = time.time()
        programs_amount = options["programs_amount"]

        pool = multiprocessing.Pool(processes=7)
        pool.map(
            self._generate_program_with_dependencies,
            repeat(options, programs_amount),
        )
        pool.close()
        pool.join()

        self.stdout.write(
            f"Generated fixtures in {(time.time() - start_time)} seconds"
        )
