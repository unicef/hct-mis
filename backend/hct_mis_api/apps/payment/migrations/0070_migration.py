# Generated by Django 3.2.15 on 2022-09-14 07:38

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0069_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialserviceprovider',
            name='distribution_limit',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, help_text='The maximum amount of money that can be distributed or unlimited if null', max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
    ]
