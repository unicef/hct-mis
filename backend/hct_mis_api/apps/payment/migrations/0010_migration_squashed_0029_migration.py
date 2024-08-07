# Generated by Django 3.2.19 on 2023-06-08 19:44

import concurrency.fields
from decimal import Decimal
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
def change_all_rapidpro_to_pending(apps, schema_editor):
    CashPlanPaymentVerification = apps.get_model("payment", "CashPlanPaymentVerification")
    CashPlanPaymentVerification.objects.filter(
        verification_method="RAPIDPRO",
    ).update(status="PENDING")

def empty_reverse(apps, schema_editor):
    pass

def populate_existing_payment_record_usd_amount(apps, schema_editor):
    PaymentRecord = apps.get_model("payment", "PaymentRecord")
    all_payment_records = PaymentRecord.objects.all()

    for payment_record in all_payment_records:
        exchange_rate = payment_record.cash_plan.exchange_rate if payment_record.cash_plan else None
        if exchange_rate:
            payment_record.delivered_quantity_usd = Decimal(payment_record.delivered_quantity * exchange_rate).quantize(
                Decimal(".01")
            )
    PaymentRecord.objects.bulk_update(all_payment_records, ["delivered_quantity_usd"])

def fill_in_registration_ca_id(apps, schema_editor):
    pass


def assign_valid_delivered_quantity(apps, schema_editor):
    PaymentRecord = apps.get_model("payment", "PaymentRecord")
    all_payment_records = PaymentRecord.objects.all()

    payment_records_to_update = []
    for payment_record in all_payment_records:
        if payment_record.currency == "USD":
            payment_record.delivered_quantity_usd = payment_record.delivered_quantity
            payment_records_to_update.append(payment_record)

    PaymentRecord.objects.bulk_update(payment_records_to_update, ["delivered_quantity_usd"])

class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_migration_squashed_0009_migration'),
        ('household', '0003_migration_squashed_0086_migration'),
        ('program', '0002_migration_squashed_0020_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentverification',
            name='received_amount',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='transaction_reference_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='vision_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='cashplanpaymentverification',
            name='confidence_interval',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='cashplanpaymentverification',
            name='margin_of_error',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='cashplanpaymentverification',
            name='rapid_pro_flow_id',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='cashplanpaymentverification',
            name='sampling',
            field=models.CharField(choices=[('FULL_LIST', 'Full list'), ('RANDOM', 'Random sampling')], max_length=50),
        ),
        migrations.AlterField(
            model_name='paymentverification',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('RECEIVED', 'RECEIVED'), ('NOT_RECEIVED', 'NOT RECEIVED'), ('RECEIVED_WITH_ISSUES', 'RECEIVED WITH ISSUES')], default='PENDING', max_length=50),
        ),
        migrations.AddField(
            model_name='cashplanpaymentverification',
            name='rapid_pro_flow_start_uuid',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='cashplanpaymentverification',
            name='age_filter',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='cashplanpaymentverification',
            name='excluded_admin_areas_filter',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='cashplanpaymentverification',
            name='sex_filter',
            field=models.CharField(max_length=10, null=True, blank=True),
        ),
        migrations.RunPython(change_all_rapidpro_to_pending, empty_reverse),
        migrations.AddField(
            model_name='cashplanpaymentverification',
            name='activation_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='cashplanpaymentverification',
            name='completion_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=0, help_text='record revision number'),
        ),
        migrations.AddField(
            model_name='paymentverification',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=0, help_text='record revision number'),
        ),
        migrations.AddField(
            model_name='cashplanpaymentverification',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=0, help_text='record revision number'),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='delivered_quantity_usd',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.RunPython(populate_existing_payment_record_usd_amount, empty_reverse),
        migrations.AddField(
            model_name='paymentrecord',
            name='head_of_household',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_records', to='household.individual'),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='delivery_type',
            field=models.CharField(choices=[('CASH', 'Cash'), ('DEPOSIT_TO_CARD', 'Deposit to Card'), ('TRANSFER', 'Transfer')], max_length=20),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='entitlement_card_issue_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='entitlement_card_number',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='entitlement_card_status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='status',
            field=models.CharField(choices=[('SUCCESS', 'Success'), ('PENDING', 'Pending'), ('ERROR', 'Error')], max_length=255),
        ),
        migrations.AlterField(
            model_name='cashplanpaymentverification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='cashplanpaymentverification',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('ACTIVE', 'Active'), ('FINISHED', 'Finished')], db_index=True, default='PENDING', max_length=50),
        ),
        migrations.AlterField(
            model_name='cashplanpaymentverification',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='paymentverification',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='paymentverification',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='serviceprovider',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='delivery_type',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'), ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'), ('Deposit to Card', 'Deposit to Card'), ('In Kind', 'In Kind'), ('Mobile Money', 'Mobile Money'), ('Other', 'Other'), ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'), ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'), ('Voucher', 'Voucher')], max_length=24),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='status',
            field=models.CharField(choices=[('Transaction Successful', 'Transaction Successful'), ('Transaction Pending', 'Transaction Pending'), ('Transaction Erroneous', 'Transaction Erroneous')], max_length=255),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='registration_ca_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.RunPython(fill_in_registration_ca_id, empty_reverse),
        migrations.AlterField(
            model_name='paymentverification',
            name='status_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='status',
            field=models.CharField(choices=[('Transaction Successful', 'Transaction Successful'), ('Transaction Erroneous', 'Transaction Erroneous'), ('Distribution Successful', 'Distribution Successful'), ('Not Distributed', 'Not Distributed')], max_length=255),
        ),
        migrations.RunPython(assign_valid_delivered_quantity, empty_reverse),
        migrations.AlterField(
            model_name='paymentrecord',
            name='delivery_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='ca_id',
            field=models.CharField(db_index=True, max_length=255, null=True),
        ),
    ]
