# Generated by Django 2.2.8 on 2020-03-16 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("targeting", "0003_migration"),
    ]

    def clear_target_populations(apps, schema):
        TargetPopulation = apps.get_model("targeting", "TargetPopulation")
        TargetPopulation.objects.all().delete()

    operations = [
        migrations.RunPython(clear_target_populations),
        migrations.AlterField(
            model_name="targetpopulation",
            name="name",
            field=models.TextField(unique=True),
        ),
    ]
