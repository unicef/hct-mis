# Generated by Django 2.2.8 on 2020-05-22 11:45

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cash_assist_datahub', '0001_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(choices=[('MIS', 'HCT-MIS'), ('CA', 'Cash Assist')], max_length=3)),
                ('status', models.CharField(choices=[('NEW', 'New'), ('READY', 'Ready'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], max_length=11)),
                ('last_modified_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TargetPopulation',
            fields=[
                ('mis_id', models.UUIDField(unique=True)),
                ('ca_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('ca_hash_id', models.UUIDField(unique=True)),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cash_assist_datahub.Session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceProvider',
            fields=[
                ('business_area', models.CharField(max_length=20)),
                ('ca_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=255)),
                ('short_name', models.CharField(max_length=4)),
                ('country', models.CharField(max_length=3)),
                ('vision_id', models.CharField(max_length=255)),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cash_assist_datahub.Session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Programme',
            fields=[
                ('mis_id', models.UUIDField(unique=True)),
                ('ca_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('ca_hash_id', models.CharField(max_length=255, unique=True)),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cash_assist_datahub.Session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PaymentRecord',
            fields=[
                ('business_area', models.CharField(max_length=20)),
                ('status', models.CharField(choices=[('SUCCESS', 'Sucess'), ('PENDING', 'Pending'), ('ERROR', 'Error')], max_length=255)),
                ('status_date', models.DateTimeField()),
                ('ca_id', models.CharField(max_length=255)),
                ('ca_hash_id', models.UUIDField(primary_key=True, serialize=False)),
                ('registration_ca_id', models.CharField(max_length=255)),
                ('household_mis_id', models.UUIDField()),
                ('focal_point_mis_id', models.UUIDField()),
                ('full_name', models.CharField(max_length=255)),
                ('total_persons_covered', models.IntegerField()),
                ('distribution_modality', models.CharField(max_length=255)),
                ('target_population_mis_id', models.UUIDField()),
                ('target_population_cash_assist_id', models.CharField(max_length=255)),
                ('entitlement_card_number', models.CharField(max_length=255)),
                ('entitlement_card_status', models.CharField(choices=[('SUCCESS', 'Sucess'), ('PENDING', 'Pending'), ('ERROR', 'Error')], default='ACTIVE', max_length=20)),
                ('entitlement_card_issue_date', models.DateField()),
                ('delivery_type', models.CharField(choices=[('CASH', 'Cash'), ('DEPOSIT_TO_CARD', 'Deposit to Card'), ('TRANSFER', 'Transfer')], default='ACTIVE', max_length=20)),
                ('currency', models.CharField(max_length=4)),
                ('entitlement_quantity', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('delivered_quantity', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('delivery_date', models.DateTimeField()),
                ('service_provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_records', to='cash_assist_datahub.ServiceProvider')),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cash_assist_datahub.Session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CashPlan',
            fields=[
                ('business_area', models.CharField(max_length=20)),
                ('cash_plan_id', models.CharField(max_length=255)),
                ('cash_plan_hash_id', models.UUIDField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('Distribution Completed', 'Distribution Completed'), ('Distribution Completed with Errors', 'Distribution Completed with Errors'), ('Transaction Completed', 'Transaction Completed'), ('Transaction Completed with Errors', 'Transaction Completed with Errors')], max_length=255)),
                ('status_date', models.DateTimeField()),
                ('name', models.CharField(max_length=255)),
                ('distribution_level', models.CharField(max_length=255)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('dispersion_date', models.DateTimeField()),
                ('coverage_duration', models.PositiveIntegerField()),
                ('coverage_unit', models.CharField(max_length=255)),
                ('comments', models.CharField(max_length=255)),
                ('program_mis_id', models.UUIDField()),
                ('delivery_type', models.CharField(max_length=255)),
                ('assistance_measurement', models.CharField(max_length=255)),
                ('assistance_through', models.CharField(max_length=255)),
                ('vision_id', models.CharField(max_length=255)),
                ('funds_commitment', models.CharField(max_length=255)),
                ('down_payment', models.CharField(max_length=255)),
                ('validation_alerts_count', models.IntegerField()),
                ('total_persons_covered', models.IntegerField()),
                ('total_persons_covered_revised', models.IntegerField()),
                ('payment_records_count', models.IntegerField()),
                ('total_entitled_quantity', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('total_entitled_quantity_revised', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('total_delivered_quantity', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('total_undelivered_quantity', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cash_assist_datahub.Session')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
