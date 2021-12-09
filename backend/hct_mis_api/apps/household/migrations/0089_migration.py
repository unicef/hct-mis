# Generated by Django 2.2.16 on 2021-11-30 15:54

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('registration_data', '0018_migration'),
        ('core', '0043_migration'),
        ('household', '0088_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='XlsxUpdateFile',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('file', models.FileField(upload_to='')),
                ('xlsx_match_columns', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=32), size=None)),
                ('business_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.BusinessArea')),
                ('rdi', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registration_data.RegistrationDataImport')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
