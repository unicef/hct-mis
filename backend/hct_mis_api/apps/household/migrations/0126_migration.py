# Generated by Django 3.2.15 on 2022-10-03 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0125_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documenttype',
            options={'ordering': ['label']},
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='type',
            field=models.CharField(choices=[('BIRTH_CERTIFICATE', 'Birth Certificate'), ('DRIVERS_LICENSE', "Driver's License"), ('ELECTORAL_CARD', 'Electoral Card'), ('NATIONAL_ID', 'National ID'), ('NATIONAL_PASSPORT', 'National Passport'), ('TAX_ID', 'Tax Number Identification'), ('RESIDENCE_PERMIT_NO', "Foreigner's Residence Permit"), ('OTHER', 'Other')], max_length=50, unique=True),
        ),
        migrations.RemoveField(
            model_name='documenttype',
            name='country',
        ),
    ]
