# Generated by Django 3.2.15 on 2023-01-27 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_module', '0008_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentplan',
            name='exchange_rate',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=12, null=True),
        ),
    ]
