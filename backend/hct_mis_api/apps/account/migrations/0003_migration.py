# Generated by Django 2.2.8 on 2020-09-25 14:06

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='permissions',
            field=account.models.ChoiceArrayField(base_field=models.CharField(choices=[('DASHBOARD.READ', 'DASHBOARD.READ'), ('RDI.READ', 'RDI.READ'), ('PERMISSION_RDI_IMPORT.CREATE', 'PERMISSION_RDI_IMPORT.CREATE'), ('PERMISSION_RDI_IMPORT.READ', 'PERMISSION_RDI_IMPORT.READ'), ('PERMISSION_RDI_MERGE.RUN', 'PERMISSION_RDI_MERGE.RUN'), ('PERMISSION_RDI_RERUN_DEDUPLICATION.RUN', 'PERMISSION_RDI_RERUN_DEDUPLICATION.RUN'), ('PERMISSION_RDI_KOBO.CREATE', 'PERMISSION_RDI_KOBO.CREATE'), ('PERMISSION_RDI_XLSX.CREATE', 'PERMISSION_RDI_XLSX.CREATE'), ('PERMISSION_PROGRAM.LIST', 'PERMISSION_PROGRAM.LIST'), ('PERMISSION_PROGRAM.READ', 'PERMISSION_PROGRAM.READ'), ('PERMISSION_PROGRAM.CREATE', 'PERMISSION_PROGRAM.CREATE'), ('PERMISSION_PROGRAM.UPDATE', 'PERMISSION_PROGRAM.UPDATE'), ('PERMISSION_PROGRAM.DELETE', 'PERMISSION_PROGRAM.DELETE')], max_length=255), size=None),
        ),
    ]
