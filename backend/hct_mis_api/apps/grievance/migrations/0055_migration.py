# Generated by Django 3.2.15 on 2023-02-27 13:00

from decimal import Decimal

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0054_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketpaymentverificationdetails',
            name='old_received_amount',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
    ]
