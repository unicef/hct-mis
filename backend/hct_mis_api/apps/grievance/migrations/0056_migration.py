# Generated by Django 3.2.15 on 2022-09-27 17:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('grievance', '0055_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrievanceDocument',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='grievance_documents')),
                ('file_size', models.IntegerField(null=True)),
                ('content_type', models.CharField(max_length=100)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('grievance_ticket', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='support_documents', to='grievance.grievanceticket')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
