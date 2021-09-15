# Generated by Django 2.2.16 on 2021-09-15 09:28

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0082_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individual',
            name='deduplication_batch_results',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='individual',
            name='deduplication_golden_record_results',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='individual',
            name='imported_individual_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
