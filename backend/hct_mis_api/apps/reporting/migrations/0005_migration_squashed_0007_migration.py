# Generated by Django 3.2.19 on 2023-06-09 07:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hct_mis_api.apps.account.fields
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    replaces = [('reporting', '0005_migration'), ('reporting', '0006_migration'), ('reporting', '0007_migration')]

    dependencies = [
        ('core', '0016_migration'),
        ('reporting', '0001_migration_squashed_0004_migration'),
        ('program', '0019_migration'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardReport',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Processing'), (2, 'Generated'), (3, 'Failed')], default=1)),
                ('report_type', hct_mis_api.apps.account.fields.ChoiceArrayField(base_field=models.CharField(choices=[('TOTAL_TRANSFERRED_BY_COUNTRY', 'Total transferred by country'), ('TOTAL_TRANSFERRED_BY_ADMIN_AREA', 'Total transferred by admin area'), ('BENEFICIARIES_REACHED', 'Beneficiaries reached'), ('INDIVIDUALS_REACHED', 'Individuals reached drilldown'), ('VOLUME_BY_DELIVERY_MECHANISM', 'Volume by delivery mechanism'), ('GRIEVANCES_AND_FEEDBACK', 'Grievances and Feedback'), ('PROGRAMS', 'Programmes'), ('PAYMENT_VERIFICATION', 'Payment verification')], max_length=255), size=None)),
                ('year', models.PositiveSmallIntegerField(default=2021)),
                ('admin_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_reports', to='core.adminarea')),
                ('business_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_reports', to='core.businessarea')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_reports', to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_reports', to='program.program')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
