# Generated by Django 2.2.16 on 2021-01-07 22:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0006_migration'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('program', '0015_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('status', models.IntegerField(choices=[(1, 'Processing'), (2, 'Generated'), (3, 'Failed')], default=1)),
                ('report_type', models.IntegerField(choices=[(1, 'Individuals'), (2, 'Household Demographics'), (3, 'Cash Plan Verification'), (4, 'Payments'), (5, 'Payment verification'), (6, 'Cash Plan'), (7, 'Program'), (8, 'Individuals and Payment')])),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('admin_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='core.AdminArea')),
                ('business_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='core.BusinessArea')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='program.Program')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
