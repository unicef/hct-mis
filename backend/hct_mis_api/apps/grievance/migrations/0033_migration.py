# Generated by Django 2.2.16 on 2021-09-19 17:38

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0032_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='grievanceticket',
            name='extras',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]
