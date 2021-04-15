# Generated by Django 2.2.16 on 2021-04-15 20:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hct_mis_api.apps.account.models
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_migration'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('program', '0001_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('status', models.IntegerField(choices=[(1, 'Processing'), (2, 'Generated'), (3, 'Failed')], default=1)),
                ('report_type', models.IntegerField(choices=[(1, 'Individuals'), (2, 'Households'), (3, 'Cash Plan Verification'), (4, 'Payments'), (5, 'Payment verification'), (6, 'Cash Plan'), (7, 'Programme'), (8, 'Individuals & Payment')])),
                ('date_from', models.DateField()),
                ('date_to', models.DateField()),
                ('number_of_records', models.IntegerField(blank=True, null=True)),
                ('admin_area', models.ManyToManyField(blank=True, related_name='reports', to='core.AdminArea')),
                ('business_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='core.BusinessArea')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='program.Program')),
            ],
            options={
                'ordering': ['-created_at', 'report_type', 'status', 'created_by'],
            },
        ),
        migrations.CreateModel(
            name='DashboardReport',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Processing'), (2, 'Generated'), (3, 'Failed')], default=1)),
                ('report_type', hct_mis_api.apps.account.models.ChoiceArrayField(base_field=models.CharField(choices=[('TOTAL_TRANSFERRED_BY_COUNTRY', 'Total transferred by country'), ('TOTAL_TRANSFERRED_BY_ADMIN_AREA', 'Total transferred by admin area'), ('BENEFICIARIES_REACHED', 'Beneficiaries reached'), ('INDIVIDUALS_REACHED', 'Individuals reached drilldown'), ('VOLUME_BY_DELIVERY_MECHANISM', 'Volume by delivery mechanism'), ('GRIEVANCES_AND_FEEDBACK', 'Grievances and Feedback'), ('PROGRAMS', 'Programmes'), ('PAYMENT_VERIFICATION', 'Payment verification')], max_length=255), size=None)),
                ('year', models.PositiveSmallIntegerField(default=2021)),
                ('admin_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_reports', to='core.AdminArea')),
                ('business_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_reports', to='core.BusinessArea')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_reports', to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_reports', to='program.Program')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
