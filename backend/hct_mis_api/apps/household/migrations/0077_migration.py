# Generated by Django 2.2.16 on 2021-06-30 12:27

from django.db import migrations
from django.db.models import Case, When, Q, Value

from hct_mis_api.apps.household.models import NOT_DISABLED, DISABLED, LOT_DIFFICULTY, CANNOT_DO


def set_disability(apps, schema_editor):
    Individual = apps.get_model("household", "Individual")

    Individual.objects.all().update(disability=Case(
        When(Q(seeing_disability=LOT_DIFFICULTY) | Q(seeing_disability=CANNOT_DO), then=Value(DISABLED)),
        When(Q(hearing_disability=LOT_DIFFICULTY) | Q(hearing_disability=CANNOT_DO), then=Value(DISABLED)),
        When(Q(physical_disability=LOT_DIFFICULTY) | Q(physical_disability=CANNOT_DO), then=Value(DISABLED)),
        When(Q(memory_disability=LOT_DIFFICULTY) | Q(memory_disability=CANNOT_DO), then=Value(DISABLED)),
        When(Q(selfcare_disability=LOT_DIFFICULTY) | Q(selfcare_disability=CANNOT_DO), then=Value(DISABLED)),
        When(Q(comms_disability=LOT_DIFFICULTY) | Q(comms_disability=CANNOT_DO), then=Value(DISABLED)),
        default=Value(NOT_DISABLED)
    ))


def empty_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0076_migration'),
    ]

    operations = [
        migrations.RunPython(set_disability, empty_reverse)
    ]
