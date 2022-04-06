# Generated by Django 3.2.12 on 2022-04-06 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mis_datahub', '0038_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='type',
            field=models.CharField(choices=[('BIRTH_CERTIFICATE', 'Birth Certificate'), ('DRIVERS_LICENSE', "Driver's License"), ('ELECTORAL_CARD', 'Electoral Card'), ('NATIONAL_ID', 'National ID'), ('NATIONAL_PASSPORT', 'National Passport'), ('TAX_ID', 'Tax Number Identification'), ('RESIDENCE_PERMIT_NO', "Foreigner's Residence Permit"), ('OTHER', 'Other')], max_length=50),
        ),
    ]
