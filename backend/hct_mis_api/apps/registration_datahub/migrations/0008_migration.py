# Generated by Django 2.2.8 on 2020-03-10 14:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("registration_datahub", "0007_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="importedhousehold",
            name="registration_date",
            field=models.DateField(
                null=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]