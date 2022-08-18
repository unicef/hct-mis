# Generated by Django 3.2.13 on 2022-08-18 10:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payment', '0057_migration'),
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
    ]
