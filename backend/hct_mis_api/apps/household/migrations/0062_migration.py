# Generated by Django 2.2.16 on 2021-05-04 11:57

from django.db import migrations


def set_sys_field(individual, key, value):
    if "sys" not in individual.user_fields:
        individual.user_fields["sys"] = {}
    individual.user_fields["sys"][key] = value


def fix_muac_flex_field(apps, schema_editor):
    Individual = apps.get_model("household", "Individual")
    for individual in Individual.objects.filter(flex_fields__has_key="muac_i_f"):
        muac = individual.flex_fields.get("muac_i_f")
        if muac is None:
            continue
        set_sys_field(individual, "old_muac", muac)
        if isinstance(muac, str):
            muac = float(muac)
        if muac > 27:
            muac /= 10
        muac = str(muac)
        individual.flex_fields["muac_i_f"] = muac
        individual.save()


def empty_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("household", "0061_migration"),
    ]

    operations = [
        migrations.RunPython(fix_muac_flex_field, empty_reverse),
    ]
