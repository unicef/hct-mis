# Generated by Django 2.2.16 on 2021-12-01 14:06

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0089_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xlsxupdatefile',
            name='xlsx_match_columns',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=32), null=True, size=None),
        ),
    ]
