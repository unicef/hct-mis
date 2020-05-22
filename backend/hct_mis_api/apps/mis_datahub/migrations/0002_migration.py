# Generated by Django 2.2.8 on 2020-05-22 11:45

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mis_datahub', '0001_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Household',
            fields=[
                ('mis_id', models.UUIDField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('INACTIVE', 'Inactive'), ('ACTIVE', 'Active')], max_length=50)),
                ('household_size', models.PositiveIntegerField()),
                ('government_form_number', models.CharField(max_length=255, null=True)),
                ('form_number', models.CharField(max_length=255, null=True)),
                ('agency_id', models.CharField(max_length=255, null=True)),
                ('address', models.CharField(max_length=255, null=True)),
                ('admin1', models.CharField(max_length=255, null=True)),
                ('admin2', models.CharField(max_length=255, null=True)),
                ('country', django_countries.fields.CountryField(max_length=2, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('mis_id', models.UUIDField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('INACTIVE', 'Inactive'), ('ACTIVE', 'Active')], max_length=50, null=True)),
                ('full_name', models.CharField(max_length=255)),
                ('family_name', models.CharField(max_length=255, null=True)),
                ('given_name', models.CharField(max_length=255, null=True)),
                ('middle_name', models.CharField(max_length=255, null=True)),
                ('sex', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], max_length=255)),
                ('date_of_birth', models.DateField()),
                ('estimated_date_of_birth', models.BooleanField()),
                ('relationship', models.CharField(choices=[('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('HEAD', 'Head of household (self)'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('BROTHER_SISTER', 'Brother / Sister'), ('MOTHER_FATHER', 'Mother / Father'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('COUSIN', 'Cousin')], max_length=255, null=True)),
                ('role', models.CharField(choices=[('PRIMARY', 'Primary collector'), ('ALTERNATE', 'Alternate collector'), ('NO_ROLE', 'None')], max_length=255, null=True)),
                ('marital_status', models.CharField(choices=[('SINGLE', 'SINGLE'), ('MARRIED', 'Married'), ('WIDOW', 'Widow'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated')], max_length=255)),
                ('phone_number', models.CharField(max_length=14, null=True)),
                ('household', models.ForeignKey(db_column='household_mis_id', on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.Household')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('program_id', models.UUIDField(primary_key=True, serialize=False)),
                ('business_area', models.CharField(max_length=20)),
                ('program_ca_id', models.CharField(max_length=255)),
                ('program_ca_hash_id', models.CharField(max_length=255)),
                ('programme_name', models.CharField(max_length=255)),
                ('scope', models.PositiveIntegerField()),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('description', models.CharField(max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
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
                ('mis_id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('population_type', models.CharField(default='HOUSEHOLD', max_length=20)),
                ('targeting_criteria', models.TextField()),
                ('active_households', models.PositiveIntegerField(default=0)),
                ('program', models.ForeignKey(db_column='program_mis_id', on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.Program')),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.Session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TargetPopulationEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ca_household_id', models.CharField(max_length=255)),
                ('vulnerability_score', models.DecimalField(blank=True, decimal_places=3, help_text='Written by a tool such as Corticon.', max_digits=6, null=True)),
                ('household', models.ForeignKey(db_column='household_mis_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.Household')),
                ('individual', models.ForeignKey(db_column='individual_mis_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.Individual')),
                ('session_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.Session')),
                ('target_population', models.ForeignKey(db_column='target_population_mis_id', on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.TargetPopulation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='program',
            name='session_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.Session'),
        ),
        migrations.AddField(
            model_name='individual',
            name='session_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.Session'),
        ),
        migrations.AddField(
            model_name='household',
            name='focal_point',
            field=models.ForeignKey(db_column='focal_point_mis_id', on_delete=django.db.models.deletion.CASCADE, related_name='heading_household', to='mis_datahub.Individual'),
        ),
        migrations.AddField(
            model_name='household',
            name='session_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.Session'),
        ),
    ]
