# Generated by Django 3.2.15 on 2022-09-21 13:33

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0070_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialserviceprovider',
            name='distribution_limit',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, help_text='The maximum amount of money in USD that can be distributed or unlimited if null', max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='assigned_payment_channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='payment.paymentchannel'),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='status',
            field=django_fsm.FSMField(choices=[('OPEN', 'Open'), ('LOCKED', 'Locked'), ('LOCKED_FSP', 'Locked FSP'), ('IN_APPROVAL', 'In Approval'), ('IN_AUTHORIZATION', 'In Authorization'), ('IN_REVIEW', 'In Review'), ('ACCEPTED', 'Accepted'), ('RECONCILED', 'Reconciled')], db_index=True, default='OPEN', max_length=50),
        ),
        migrations.RemoveField(
            model_name='deliverymechanismperpaymentplan',
            name='entitlement_quantity',
        ),
        migrations.RemoveField(
            model_name='deliverymechanismperpaymentplan',
            name='entitlement_quantity_usd',
        ),
    ]
