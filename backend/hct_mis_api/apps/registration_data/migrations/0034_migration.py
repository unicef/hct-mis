# Generated by Django 3.2.25 on 2024-05-26 15:21

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0176_migration'),
        ('registration_data', '0033_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportData',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('RUNNING', 'Running'), ('FINISHED', 'Finished'), ('ERROR', 'Error'), ('VALIDATION_ERROR', 'Validation Error')], default='FINISHED', max_length=20)),
                ('business_area_slug', models.CharField(blank=True, max_length=200)),
                ('file', models.FileField(null=True, upload_to='')),
                ('data_type', models.CharField(choices=[('XLSX', 'XLSX File'), ('JSON', 'JSON File'), ('FLEX', 'Flex Registration')], default='XLSX', max_length=4)),
                ('number_of_households', models.PositiveIntegerField(null=True)),
                ('number_of_individuals', models.PositiveIntegerField(null=True)),
                ('error', models.TextField(blank=True)),
                ('validation_errors', models.TextField(blank=True)),
                ('created_by_id', models.UUIDField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='KoboImportData',
            fields=[
                ('importdata_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='registration_data.importdata')),
                ('kobo_asset_id', models.CharField(max_length=100)),
                ('only_active_submissions', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('registration_data.importdata',),
        ),
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
        migrations.CreateModel(
            name='KoboImportedSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('kobo_submission_uuid', models.UUIDField()),
                ('kobo_asset_id', models.CharField(max_length=150)),
                ('kobo_submission_time', models.DateTimeField()),
                ('amended', models.BooleanField(blank=True, default=False)),
                ('imported_household', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='household.household')),
                ('registration_data_import', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registration_data.registrationdataimportdatahub')),
            ],
        ),
    ]
