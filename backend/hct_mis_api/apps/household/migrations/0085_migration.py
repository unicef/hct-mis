# Generated by Django 2.2.16 on 2021-09-23 11:48

from django.db import migrations

from hct_mis_api.apps.core.field_attributes.fields_types import TYPE_DECIMAL
from hct_mis_api.apps.core.utils import serialize_flex_attributes, fix_flex_type_fields


def fix_fields_individuals(apps, schema_editor):
    Individual = apps.get_model("household", "Individual")
    individuals = Individual.objects.all()

    all_flex_fields = serialize_flex_attributes().get("individuals", {})
    if all_flex_fields and individuals:
        decimal_flex_fields = [key for key, value in all_flex_fields.items() if value["type"] == TYPE_DECIMAL]

        individuals = fix_flex_type_fields(individuals, decimal_flex_fields)
        Individual.objects.bulk_update(individuals, ("flex_fields",), 1000)


def fix_fields_households(apps, schema_editor):
    Household = apps.get_model("household", "Household")
    households = Household.objects.all()

    all_flex_fields = serialize_flex_attributes().get("households", {})
    if all_flex_fields and households:
        decimal_flex_fields = [key for key, value in all_flex_fields.items() if value["type"] == TYPE_DECIMAL]

        households = fix_flex_type_fields(households, decimal_flex_fields)
        Household.objects.bulk_update(households, ("flex_fields",), 1000)


class Migration(migrations.Migration):

    dependencies = [
        ("household", "0084_migration"),
    ]

    operations = [
        migrations.RunPython(fix_fields_individuals, migrations.RunPython.noop),
        migrations.RunPython(fix_fields_households, migrations.RunPython.noop),
    ]
