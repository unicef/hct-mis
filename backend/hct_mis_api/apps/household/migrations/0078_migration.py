# Generated by Django 2.2.16 on 2021-07-06 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0077_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documenttype',
            name='type',
            field=models.CharField(choices=[('BIRTH_CERTIFICATE', 'Birth Certificate'), ('DRIVERS_LICENSE', "Driver's License"), ('NATIONAL_ID', 'National ID'), ('NATIONAL_PASSPORT', 'National Passport'), ('ELECTORAL_CARD', 'Electoral Card'), ('OTHER', 'Other'), ('NOT_AVAILABLE', 'Not Available'), ('UNHCR_ID', 'Unhcr ID'), ('SCOPE_ID', 'Scope ID')], max_length=50),
        ),
    ]
