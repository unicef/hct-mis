# Generated by Django 3.2.15 on 2022-11-04 14:17

from django.db import migrations, models, transaction
from hct_mis_api.apps.utils.phone import calculate_phone_numbers_validity


@transaction.atomic
def update_each_phone_numbers_validity(apps, schema_editor):
    ImportedIndividual = apps.get_model("registration_datahub", "ImportedIndividual")
    for individual in ImportedIndividual.objects.all():
        calculate_phone_numbers_validity(individual)
        individual.save(update_fields=["phone_no_valid", "phone_no_alternative_valid"])


class Migration(migrations.Migration):

    dependencies = [
        ("registration_datahub", "0082_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="importedindividual",
            name="phone_no_alternative_valid",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="importedindividual",
            name="phone_no_valid",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(update_each_phone_numbers_validity),
    ]
