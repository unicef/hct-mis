# Generated by Django 3.2.15 on 2022-11-08 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0078_migration'),
    ]

    operations = [
        migrations.DeleteModel(
            name='XlsxPaymentVerificationPlanFile',
        ),
    ]
