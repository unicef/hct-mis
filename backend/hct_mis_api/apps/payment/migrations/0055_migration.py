# Generated by Django 3.2.13 on 2022-08-16 13:43

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0054_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverymechanismperpaymentplan',
            name='financial_service_provider',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='delivery_mechanisms_per_payment_plan', to='payment.financialserviceprovider'),
        ),
        migrations.AlterField(
            model_name='deliverymechanismperpaymentplan',
            name='sent_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='sent_delivery_mechanisms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='financialserviceprovider',
            name='distribution_limit',
            field=models.DecimalField(db_index=True, decimal_places=2, help_text='The maximum amount of money that can be distributed or unlimited if 0', max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
    ]
