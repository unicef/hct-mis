# Generated by Django 2.2.16 on 2021-09-10 13:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0040_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='koboimportedsubmission',
            name='registration_data_import',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='registration_datahub.RegistrationDataImportDatahub'),
        ),
    ]
