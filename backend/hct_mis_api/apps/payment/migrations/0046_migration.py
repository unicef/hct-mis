# Generated by Django 3.2.13 on 2022-07-11 09:00

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
import model_utils.fields
import multiselectfield.db.fields
import uuid

import django_fsm

import hct_mis_api.apps.account.models


def populate_existing_payment_record_usd_amount(apps, schema_editor):
    PaymentRecord = apps.get_model("payment", "PaymentRecord")
    all_payment_records = PaymentRecord.objects.all()

    for payment_record in all_payment_records:
        exchange_rate = payment_record.cash_plan.exchange_rate if payment_record.cash_plan else None
        if exchange_rate:
            payment_record.entitlement_quantity_usd = Decimal(
                payment_record.entitlement_quantity * exchange_rate
            ).quantize(Decimal(".01"))

    PaymentRecord.objects.bulk_update(all_payment_records, ["entitlement_quantity_usd"])


def populate_existing_cash_plan_usd_amount(apps, schema_editor):
    CashPlan = apps.get_model("payment", "CashPlan")
    all_cash_plans = CashPlan.objects.all()

    for cash_plan in all_cash_plans:
        if cash_plan.exchange_rate:
            cash_plan.total_delivered_quantity_usd = Decimal(
                cash_plan.total_delivered_quantity * cash_plan.exchange_rate
            ).quantize(Decimal(".01"))
            cash_plan.total_undelivered_quantity_usd = Decimal(
                cash_plan.total_undelivered_quantity * cash_plan.exchange_rate
            ).quantize(Decimal(".01"))
            cash_plan.total_entitled_quantity_usd = Decimal(
                cash_plan.total_entitled_quantity * cash_plan.exchange_rate
            ).quantize(Decimal(".01"))
            cash_plan.total_entitled_quantity_revised_usd = Decimal(
                cash_plan.total_entitled_quantity_revised * cash_plan.exchange_rate
            ).quantize(Decimal(".01"))

    CashPlan.objects.bulk_update(
        all_cash_plans,
        [
            "total_delivered_quantity_usd",
            "total_undelivered_quantity_usd",
            "total_entitled_quantity_usd",
            "total_entitled_quantity_revised_usd",
        ],
    )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("program", "0033_migration"),
        ("core", "0048_migration"),
        ("household", "0109_migration"),
        ("payment", "0045_migration"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentChannel",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("delivery_data", models.JSONField(blank=True, default=dict)),
                (
                    "delivery_mechanism",
                    models.CharField(
                        choices=[
                            ("Cardless cash withdrawal", "Cardless cash withdrawal"),
                            ("Cash", "Cash"),
                            ("Cash by FSP", "Cash by FSP"),
                            ("Cheque", "Cheque"),
                            ("Deposit to Card", "Deposit to Card"),
                            ("In Kind", "In Kind"),
                            ("Mobile Money", "Mobile Money"),
                            ("Other", "Other"),
                            ("Pre-paid card", "Pre-paid card"),
                            ("Referral", "Referral"),
                            ("Transfer", "Transfer"),
                            ("Transfer to Account", "Transfer to Account"),
                            ("Voucher", "Voucher"),
                        ],
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "individual",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="household.individual"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="paymentrecord",
            name="entitlement_quantity_usd",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=12,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AlterField(
            model_name="paymentrecord",
            name="head_of_household",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to="household.individual"),
        ),
        migrations.AlterField(
            model_name="paymentrecord",
            name="household",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="household.household"),
        ),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="CashPlan",
                    fields=[
                        (
                            "id",
                            model_utils.fields.UUIDField(
                                default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                            ),
                        ),
                        ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                        ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                        ("ca_id", models.CharField(db_index=True, max_length=255, null=True)),
                        ("ca_hash_id", models.UUIDField(null=True, unique=True)),
                        (
                            "status",
                            models.CharField(
                                choices=[
                                    ("Distribution Completed", "Distribution Completed"),
                                    ("Distribution Completed with Errors", "Distribution Completed with Errors"),
                                    ("Transaction Completed", "Transaction Completed"),
                                    ("Transaction Completed with Errors", "Transaction Completed with Errors"),
                                ],
                                db_index=True,
                                max_length=255,
                            ),
                        ),
                        ("status_date", models.DateTimeField()),
                        ("name", models.CharField(db_index=True, max_length=255)),
                        ("distribution_level", models.CharField(max_length=255)),
                        ("start_date", models.DateTimeField(db_index=True)),
                        ("end_date", models.DateTimeField(db_index=True)),
                        ("dispersion_date", models.DateTimeField()),
                        ("coverage_duration", models.PositiveIntegerField()),
                        ("coverage_unit", models.CharField(max_length=255)),
                        ("comments", models.CharField(max_length=255, null=True)),
                        (
                            "delivery_type",
                            models.CharField(
                                choices=[
                                    ("Cardless cash withdrawal", "Cardless cash withdrawal"),
                                    ("Cash", "Cash"),
                                    ("Cash by FSP", "Cash by FSP"),
                                    ("Cheque", "Cheque"),
                                    ("Deposit to Card", "Deposit to Card"),
                                    ("In Kind", "In Kind"),
                                    ("Mobile Money", "Mobile Money"),
                                    ("Other", "Other"),
                                    ("Pre-paid card", "Pre-paid card"),
                                    ("Referral", "Referral"),
                                    ("Transfer", "Transfer"),
                                    ("Transfer to Account", "Transfer to Account"),
                                    ("Voucher", "Voucher"),
                                ],
                                db_index=True,
                                max_length=24,
                                null=True,
                            ),
                        ),
                        ("assistance_measurement", models.CharField(db_index=True, max_length=255)),
                        ("assistance_through", models.CharField(db_index=True, max_length=255)),
                        ("vision_id", models.CharField(max_length=255, null=True)),
                        ("funds_commitment", models.CharField(max_length=255, null=True)),
                        ("exchange_rate", models.DecimalField(blank=True, decimal_places=8, max_digits=12, null=True)),
                        ("down_payment", models.CharField(max_length=255, null=True)),
                        ("validation_alerts_count", models.IntegerField()),
                        ("total_persons_covered", models.IntegerField(db_index=True)),
                        ("total_persons_covered_revised", models.IntegerField(db_index=True)),
                        (
                            "total_entitled_quantity",
                            models.DecimalField(
                                db_index=True,
                                decimal_places=2,
                                max_digits=12,
                                null=True,
                                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                            ),
                        ),
                        (
                            "total_entitled_quantity_revised",
                            models.DecimalField(
                                db_index=True,
                                decimal_places=2,
                                max_digits=12,
                                null=True,
                                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                            ),
                        ),
                        (
                            "total_delivered_quantity",
                            models.DecimalField(
                                db_index=True,
                                decimal_places=2,
                                max_digits=12,
                                null=True,
                                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                            ),
                        ),
                        (
                            "total_undelivered_quantity",
                            models.DecimalField(
                                db_index=True,
                                decimal_places=2,
                                max_digits=12,
                                null=True,
                                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                            ),
                        ),
                        (
                            "business_area",
                            models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.businessarea"),
                        ),
                        (
                            "program",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="cash_plans",
                                to="program.program",
                            ),
                        ),
                        (
                            "service_provider",
                            models.ForeignKey(
                                null=True,
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="cash_plans",
                                to="payment.serviceprovider",
                            ),
                        ),
                    ],
                    options={
                        "verbose_name": "Cash Plan",
                        "ordering": ["created_at"],
                    },
                ),
                migrations.AlterField(
                    model_name="cashplanpaymentverification",
                    name="cash_plan",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="verifications", to="payment.cashplan"
                    ),
                ),
                migrations.AlterField(
                    model_name="cashplanpaymentverificationsummary",
                    name="cash_plan",
                    field=models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cash_plan_payment_verification_summary",
                        to="payment.cashplan",
                    ),
                ),
                migrations.AlterField(
                    model_name="paymentrecord",
                    name="cash_plan",
                    field=models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_records",
                        to="payment.cashplan",
                    ),
                ),
            ],
            database_operations=[],
        ),
        migrations.CreateModel(
            name="PaymentPlan",
            fields=[
                ("is_removed", models.BooleanField(default=False)),
                (
                    "id",
                    model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("status_date", models.DateTimeField()),
                ("start_date", models.DateTimeField(db_index=True)),
                ("end_date", models.DateTimeField(db_index=True)),
                ("exchange_rate", models.DecimalField(blank=True, decimal_places=8, max_digits=12, null=True)),
                (
                    "total_entitled_quantity",
                    models.DecimalField(
                        db_index=True,
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "total_entitled_quantity_usd",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "total_entitled_quantity_revised",
                    models.DecimalField(
                        db_index=True,
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "total_entitled_quantity_revised_usd",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "total_delivered_quantity",
                    models.DecimalField(
                        db_index=True,
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "total_delivered_quantity_usd",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "total_undelivered_quantity",
                    models.DecimalField(
                        db_index=True,
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "total_undelivered_quantity_usd",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                ("status", django_fsm.FSMField(db_index=True, default="OPEN", max_length=50)),
                (
                    "unicef_id",
                    django.contrib.postgres.fields.citext.CICharField(blank=True, db_index=True, max_length=250),
                ),
                ("currency", models.CharField(max_length=4)),
                ("dispersion_start_date", models.DateTimeField()),
                ("dispersion_end_date", models.DateTimeField()),
                ("female_children_count", models.PositiveSmallIntegerField(default=0)),
                ("male_children_count", models.PositiveSmallIntegerField(default=0)),
                ("female_adults_count", models.PositiveSmallIntegerField(default=0)),
                ("male_adults_count", models.PositiveSmallIntegerField(default=0)),
                ("total_households_count", models.PositiveSmallIntegerField(default=0)),
                ("total_individuals_count", models.PositiveSmallIntegerField(default=0)),
                (
                    "business_area",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.businessarea"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="created_payment_plans",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("program", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="program.program")),
                (
                    "target_population",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_plans",
                        to="targeting.targetpopulation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Payment Plan",
                "ordering": ["created_at"],
            },
        ),
        migrations.AddField(
            model_name="cashplan",
            name="total_delivered_quantity_usd",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=12,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AddField(
            model_name="cashplan",
            name="total_entitled_quantity_revised_usd",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=12,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AddField(
            model_name="cashplan",
            name="total_entitled_quantity_usd",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=12,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AddField(
            model_name="cashplan",
            name="total_undelivered_quantity_usd",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=12,
                null=True,
                validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
            ),
        ),
        migrations.AlterField(
            model_name="cashplan",
            name="program",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="program.program"),
        ),
        migrations.AlterField(
            model_name="paymentrecord",
            name="service_provider",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="payment.serviceprovider"),
        ),
        migrations.RunPython(populate_existing_payment_record_usd_amount, migrations.RunPython.noop),
        migrations.RunPython(populate_existing_cash_plan_usd_amount, migrations.RunPython.noop),
        migrations.CreateModel(
            name="FinancialServiceProvider",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("vision_vendor_number", models.CharField(max_length=100, unique=True)),
                (
                    "delivery_mechanisms",
                    hct_mis_api.apps.account.models.ChoiceArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("Cardless cash withdrawal", "Cardless cash withdrawal"),
                                ("Cash", "Cash"),
                                ("Cash by FSP", "Cash by FSP"),
                                ("Cheque", "Cheque"),
                                ("Deposit to Card", "Deposit to Card"),
                                ("In Kind", "In Kind"),
                                ("Mobile Money", "Mobile Money"),
                                ("Other", "Other"),
                                ("Pre-paid card", "Pre-paid card"),
                                ("Referral", "Referral"),
                                ("Transfer", "Transfer"),
                                ("Transfer to Account", "Transfer to Account"),
                                ("Voucher", "Voucher"),
                            ],
                            max_length=24,
                        ),
                        size=None,
                    ),
                ),
                (
                    "distribution_limit",
                    models.DecimalField(
                        db_index=True,
                        decimal_places=2,
                        help_text="The maximum amount of money that can be distributed or unlimited if 0",
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "communication_channel",
                    models.CharField(
                        choices=[("API", "API"), ("SFTP", "SFTP"), ("XLSX", "XLSX")], db_index=True, max_length=6
                    ),
                ),
                (
                    "data_transfer_configuration",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="JSON configuration for the data transfer mechanism",
                        null=True,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_financial_service_providers",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("is_removed", models.BooleanField(default=False)),
                (
                    "id",
                    model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Distribution Successful", "Distribution Successful"),
                            ("Not Distributed", "Not Distributed"),
                            ("Transaction Successful", "Transaction Successful"),
                            ("Transaction Erroneous", "Transaction Erroneous"),
                        ],
                        max_length=255,
                    ),
                ),
                ("status_date", models.DateTimeField()),
                (
                    "delivery_type",
                    models.CharField(
                        choices=[
                            ("Cardless cash withdrawal", "Cardless cash withdrawal"),
                            ("Cash", "Cash"),
                            ("Cash by FSP", "Cash by FSP"),
                            ("Cheque", "Cheque"),
                            ("Deposit to Card", "Deposit to Card"),
                            ("In Kind", "In Kind"),
                            ("Mobile Money", "Mobile Money"),
                            ("Other", "Other"),
                            ("Pre-paid card", "Pre-paid card"),
                            ("Referral", "Referral"),
                            ("Transfer", "Transfer"),
                            ("Transfer to Account", "Transfer to Account"),
                            ("Voucher", "Voucher"),
                        ],
                        max_length=24,
                    ),
                ),
                ("currency", models.CharField(max_length=4)),
                (
                    "entitlement_quantity",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "entitlement_quantity_usd",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "delivered_quantity",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                (
                    "delivered_quantity_usd",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        null=True,
                        validators=[django.core.validators.MinValueValidator(Decimal("0.01"))],
                    ),
                ),
                ("delivery_date", models.DateTimeField(blank=True, null=True)),
                ("transaction_reference_id", models.CharField(max_length=255, null=True)),
                ("excluded", models.BooleanField(default=False)),
                ("entitlement_date", models.DateTimeField(blank=True, null=True)),
                (
                    "business_area",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.businessarea"),
                ),
                (
                    "head_of_household",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.CASCADE, to="household.individual"
                    ),
                ),
                ("household", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="household.household")),
                (
                    "payment_plan",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="payment.paymentplan",
                    ),
                ),
                (
                    "financial_service_provider",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.CASCADE, to="payment.financialserviceprovider"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="FinancialServiceProviderXlsxTemplate",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("name", models.CharField(max_length=120, verbose_name="Name")),
                (
                    "columns",
                    multiselectfield.db.fields.MultiSelectField(
                        choices=[
                            ("payment_id", "Payment ID"),
                            ("household_id", "Household ID"),
                            ("admin_leve_2", "Admin Level 2"),
                            ("collector_name", "Collector Name"),
                            ("payment_channel", "Payment Channel (Delivery mechanism)"),
                            ("fsp_name", "FSP Name"),
                            ("entitlement_quantity", "Entitlement Quantity"),
                            ("tbd", "TBD"),
                        ],
                        default=[
                            "payment_id",
                            "household_id",
                            "admin_leve_2",
                            "collector_name",
                            "payment_channel",
                            "fsp_name",
                            "entitlement_quantity",
                        ],
                        help_text="Select the columns to include in the report",
                        max_length=101,
                        verbose_name="Columns",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_financial_service_provider_xlsx_templates",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="FinancialServiceProviderXlsxReport",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("file", models.FileField(blank=True, editable=False, null=True, upload_to="")),
                (
                    "status",
                    models.IntegerField(
                        blank=True,
                        choices=[(1, "Processing"), (2, "Generated"), (3, "Failed")],
                        db_index=True,
                        editable=False,
                        null=True,
                    ),
                ),
                (
                    "financial_service_provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="payment.financialserviceprovider",
                        verbose_name="Financial Service Provider",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="financialserviceprovider",
            name="fsp_xlsx_template",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="payment.financialserviceproviderxlsxtemplate",
                verbose_name="XLSX Template",
            ),
        ),
    ]
