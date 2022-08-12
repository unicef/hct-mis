# Generated by Django 3.2.13 on 2022-08-12 10:45

from django.db import migrations


def did_remove_some_duplicates(HouseholdSelectionModel):
    current_selections = HouseholdSelectionModel.objects.only("household", "target_population")
    for household_selection in current_selections:
        possible_duplicates = HouseholdSelectionModel.objects.filter(
            household=household_selection.household, target_population=household_selection.target_population
        )
        if possible_duplicates.count() > 1:
            to_remove = [duplicate for duplicate in possible_duplicates if duplicate.id != household_selection.id]
            for duplicate in to_remove:
                duplicate.delete()
            return True
    return False


def remove_duplicate_household_selections(apps, schema_editor):
    HouseholdSelectionModel = apps.get_model("targeting", "HouseholdSelection")
    while did_remove_some_duplicates(HouseholdSelectionModel):
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("household", "0119_migration"),
        ("targeting", "0031_migration"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="householdselection",
            options={"verbose_name": "Household Selection"},
        ),
        migrations.RunPython(remove_duplicate_household_selections),
        migrations.AlterUniqueTogether(
            name="householdselection",
            unique_together={("household", "target_population")},
        ),
    ]
