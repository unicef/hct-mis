# Generated by Django 3.2.25 on 2024-08-20 16:20

from django.db import migrations, models
import hct_mis_api.apps.payment.models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0142_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialserviceproviderxlsxtemplate',
            name='flex_fields',
            field=hct_mis_api.apps.payment.models.FlexFieldArrayField(base_field=models.CharField(blank=True, max_length=255), blank=True, default=list, size=None),
        ),
    ]
