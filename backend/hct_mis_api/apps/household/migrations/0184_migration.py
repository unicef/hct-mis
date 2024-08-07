# Generated by Django 3.2.25 on 2024-07-18 09:53

from django.db import migrations, models
import hct_mis_api.apps.core.utils


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0183_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individual',
            name='flex_fields',
            field=models.JSONField(blank=True, default=dict, encoder=hct_mis_api.apps.core.utils.FlexFieldsEncoder),
        ),
    ]
