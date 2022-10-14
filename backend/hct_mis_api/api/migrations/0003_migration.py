# Generated by Django 3.2.15 on 2022-10-02 15:35

from django.db import migrations, models
import hct_mis_api.apps.account.models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apitoken',
            name='grants',
            field=hct_mis_api.apps.account.models.ChoiceArrayField(base_field=models.CharField(choices=[('API_READ_ONLY', 'API_READ_ONLY'), ('API_RDI_UPLOAD', 'API_RDI_UPLOAD'), ('API_RDI_CREATE', 'API_RDI_CREATE'), ('API_PROGRAM_CREATE', 'API_PROGRAM_CREATE')], max_length=255), size=None),
        ),
    ]
