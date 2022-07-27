# Generated by Django 3.2.13 on 2022-07-26 13:50

from django.db import migrations


def get_last_name(individual):
    names = individual.full_name.split(" ")
    if len(names) > 1:
        return names[-1]


def set_last_name(apps, schema_editor):
    Individual = apps.get_model("household", "Individual")
    start = 10_000
    individuals = []
    i, count = 0, Individual.objects.all().count() // start + 1
    while i <= count:
        batch = Individual.objects.all().order_by("created_at")[start * i: start * (i + 1)]
        for ind in batch:
            names = ind.full_name.split(" ")
            if len(names) > 1:
                ind.last_name = names[-1]
            individuals.append(ind)
        Individual.objects.bulk_update(individuals, ["last_name"])
        individuals = []
        i += 1


def delete_last_name(apps, schema_editor):
    Individual = apps.get_model("household", "Individual")
    start = 10_000
    individuals = []
    i, count = 0, Individual.objects.all().count() // start + 1
    while i <= count:
        print(f"{i}/{count}")
        batch = Individual.objects.all().order_by("created_at")[start * i: start * (i + 1)]
        for ind in batch:
            ind.last_name = None
            individuals.append(ind)
        Individual.objects.bulk_update(individuals, ["last_name"])
        individuals = []
        i += 1


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0112_migration'),
    ]

    operations = [
        migrations.RunPython(set_last_name, delete_last_name)
    ]
