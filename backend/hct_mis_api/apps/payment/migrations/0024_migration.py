# Generated by Django 2.2.16 on 2021-02-24 19:00

from django.db import migrations, models


def fill_in_registration_ca_id(apps, schema_editor):
    pass


def empty_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0023_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="paymentrecord",
            name="registration_ca_id",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.RunPython(fill_in_registration_ca_id, empty_reverse),
    ]
