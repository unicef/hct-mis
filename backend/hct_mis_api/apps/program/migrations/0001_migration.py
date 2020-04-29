# Generated by Django 2.2.8 on 2020-04-29 08:18

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_migration'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255)])),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('ACTIVE', 'Active'), ('FINISHED', 'Finished')], max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('description', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255)])),
                ('program_ca_id', models.CharField(max_length=255)),
                ('budget', models.DecimalField(decimal_places=2, max_digits=11, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('frequency_of_payments', models.CharField(choices=[('REGULAR', 'Regular'), ('ONE_OFF', 'One-off')], max_length=50)),
                ('sector', models.CharField(choices=[('CHILD_PROTECTION', 'Child Protection'), ('EDUCATION', 'Education'), ('GENDER', 'Gender'), ('HEALTH', 'Health'), ('HIV_AIDS', 'HIV / AIDS'), ('MULTI_PURPOSE', 'Multi Purpose'), ('NUTRITION', 'Nutrition'), ('SOCIAL_POLICY', 'Social Policy'), ('WASH', 'WASH')], max_length=50)),
                ('scope', models.CharField(choices=[('FULL', 'Full'), ('PARTIAL', 'Partial'), ('NO_INTEGRATION', 'No Integration')], max_length=50)),
                ('cash_plus', models.BooleanField()),
                ('population_goal', models.PositiveIntegerField()),
                ('administrative_areas_of_implementation', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255)])),
                ('admin_areas', models.ManyToManyField(blank=True, related_name='programs', to='core.AdminArea')),
                ('business_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.BusinessArea')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CashPlan',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255)])),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('disbursement_date', models.DateTimeField()),
                ('number_of_households', models.PositiveIntegerField()),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('coverage_duration', models.PositiveIntegerField()),
                ('coverage_units', models.CharField(max_length=255)),
                ('cash_assist_id', models.CharField(max_length=255)),
                ('distribution_modality', models.CharField(max_length=255)),
                ('fsp', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('NOT_STARTED', 'NOT_STARTED'), ('STARTED', 'STARTED'), ('COMPLETE', 'COMPLETE')], max_length=50)),
                ('currency', models.CharField(max_length=255)),
                ('total_entitled_quantity', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('total_delivered_quantity', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('total_undelivered_quantity', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('dispersion_date', models.DateField()),
                ('delivery_type', models.CharField(max_length=255)),
                ('assistance_through', models.CharField(max_length=255)),
                ('fc_id', models.CharField(max_length=255)),
                ('dp_id', models.CharField(max_length=255)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cash_plans', to=settings.AUTH_USER_MODEL)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_plans', to='program.Program')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
