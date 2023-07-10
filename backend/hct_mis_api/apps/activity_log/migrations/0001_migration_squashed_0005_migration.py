# Generated by Django 3.2.19 on 2023-06-19 10:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_migration_squashed_0006_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.UUIDField(db_index=True, null=True)),
                ('action', models.CharField(choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete'), ('SOFT_DELETE', 'Soft Delete')], db_index=True, max_length=100, verbose_name='action')),
                ('changes', models.JSONField(null=True, verbose_name='change message')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='timestamp')),
                ('business_area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.businessarea')),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log_entries', to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logs', to=settings.AUTH_USER_MODEL, verbose_name='actor')),
                ('object_repr', models.TextField(blank=True)),
                ('program', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='program.program')),
            ],
            options={
                'verbose_name': 'log entry',
                'verbose_name_plural': 'log entries',
                'ordering': ['-timestamp'],
                'get_latest_by': 'timestamp',
            },
        ),
    ]
