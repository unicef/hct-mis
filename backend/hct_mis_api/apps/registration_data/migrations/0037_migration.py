# Generated by Django 3.2.25 on 2024-04-22 21:04

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('registration_data', '0036_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationDataImportDatahub',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('import_date', models.DateTimeField(auto_now_add=True)),
                ('hct_id', models.UUIDField(db_index=True, null=True)),
                ('import_done', models.CharField(choices=[('LOADING', 'Loading'), ('NOT_STARTED', 'Not Started'), ('STARTED', 'Started'), ('DONE', 'Done')], default='NOT_STARTED', max_length=15)),
                ('business_area_slug', models.CharField(blank=True, max_length=250)),
                ('import_data', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registration_data_import', to='registration_data.importdata')),
            ],
            options={
                'ordering': ('name',),
                'permissions': (['api_upload', 'Can upload'],),
            },
        ),
    ]
