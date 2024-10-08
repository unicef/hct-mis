# Generated by Django 3.2.18 on 2023-05-25 11:50

import django.core.validators
from django.core.paginator import Paginator
from django.db import migrations, models
import django.db.models.deletion
import django_fsm

import hct_mis_api.apps.payment.validators
import multiselectfield.db.fields


def populate_program_id_for_payments(apps, schema_editor):
    Payment = apps.get_model("payment", "Payment")
    payment_qs = Payment.objects.all().order_by("-created_at")

    paginator = Paginator(payment_qs, 1000)
    for page_number in paginator.page_range:
        to_update = []
        for payment in paginator.page(page_number).object_list:
            payment.program = payment.parent.program
            to_update.append(payment)

        Payment.objects.bulk_update(to_update, ["program"])

class Migration(migrations.Migration):

    dependencies = [
        ('program', '0038_migration'),
        ('payment', '0100_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='order_number',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(100000000), django.core.validators.MaxValueValidator(999999999), hct_mis_api.apps.payment.validators.payment_token_and_order_number_validator]),
        ),
        migrations.AddField(
            model_name='payment',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='program.program'),
        ),
        migrations.AddField(
            model_name='payment',
            name='token_number',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1000000), django.core.validators.MaxValueValidator(9999999), hct_mis_api.apps.payment.validators.payment_token_and_order_number_validator]),
        ),
        migrations.AlterField(
            model_name='financialserviceproviderxlsxtemplate',
            name='columns',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('payment_id', 'Payment ID'), ('household_id', 'Household ID'), ('household_size', 'Household Size'), ('collector_name', 'Collector Name'), ('payment_channel', 'Payment Channel'), ('fsp_name', 'FSP Name'), ('currency', 'Currency'), ('entitlement_quantity', 'Entitlement Quantity'), ('entitlement_quantity_usd', 'Entitlement Quantity USD'), ('delivered_quantity', 'Delivered Quantity'), ('delivery_date', 'Delivery Date'), ('reason_for_unsuccessful_payment', 'Reason for unsuccessful payment'), ('order_number', 'Order Number'), ('token_number', 'Token Number')], default=['payment_id', 'household_id', 'household_size', 'collector_name', 'payment_channel', 'fsp_name', 'currency', 'entitlement_quantity', 'entitlement_quantity_usd', 'delivered_quantity', 'delivery_date', 'reason_for_unsuccessful_payment', 'order_number', 'token_number'], help_text='Select the columns to include in the report', max_length=250, verbose_name='Columns'),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='status',
            field=django_fsm.FSMField(choices=[('PREPARING', 'Preparing'), ('OPEN', 'Open'), ('LOCKED', 'Locked'), ('LOCKED_FSP', 'Locked FSP'), ('IN_APPROVAL', 'In Approval'), ('IN_AUTHORIZATION', 'In Authorization'), ('IN_REVIEW', 'In Review'), ('ACCEPTED', 'Accepted'), ('FINISHED', 'Finished')], db_index=True, default='OPEN', max_length=50),
        ),
        migrations.AddConstraint(
            model_name='payment',
            constraint=models.UniqueConstraint(condition=models.Q(('is_removed', False)), fields=('program_id', 'order_number'), name='order_number_unique_per_program'),
        ),
        migrations.AddConstraint(
            model_name='payment',
            constraint=models.UniqueConstraint(condition=models.Q(('is_removed', False)), fields=('program_id', 'token_number'), name='token_number_unique_per_program'),
        ),
        migrations.RunPython(populate_program_id_for_payments, migrations.RunPython.noop),
    ]
