# Generated by Django 3.2.15 on 2022-11-08 16:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("registration_datahub", "0085_migration"),
    ]

    operations = [
        migrations.RemoveField(
            model_name='importedindividualidentity',
            name='agency',
        ),
        migrations.DeleteModel(
            name='ImportedAgency',
        ),
    ]
