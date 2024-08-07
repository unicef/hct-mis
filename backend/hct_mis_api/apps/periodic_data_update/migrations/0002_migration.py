# Generated by Django 3.2.25 on 2024-07-08 15:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('periodic_data_update', '0001_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodicDataUpdateUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('status', models.CharField(choices=[('PROCESSING', 'Processing'), ('SUCCESSFUL', 'Successful'), ('FAILED', 'Failed')], default='PROCESSING', max_length=20)),
                ('file', models.FileField(upload_to='')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='periodic_data_update_uploads', to=settings.AUTH_USER_MODEL)),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploads', to='periodic_data_update.periodicdataupdatetemplate')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
