# Generated by Django 3.2.12 on 2022-05-12 10:33

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import sorl.thumbnail.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0062_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiiaHousehold',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('rec_id', models.CharField(blank=True, default='', max_length=20)),
                ('vpo_doc', sorl.thumbnail.fields.ImageField(blank=True, upload_to='', validators=[django.core.validators.validate_image_file_extension])),
                ('vpo_doc_id', models.CharField(blank=True, default='', max_length=128)),
                ('vpo_doc_date', models.DateField(blank=True)),
                ('address', models.CharField(blank=True, default='', max_length=255)),
                ('consent', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DiiaIndividual',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('individual_id', models.CharField(blank=True, max_length=128)),
                ('last_name', models.CharField(blank=True, default='', max_length=85)),
                ('first_name', models.CharField(blank=True, default='', max_length=85)),
                ('second_name', models.CharField(blank=True, default='', max_length=85)),
                ('relationship', models.CharField(blank=True, choices=[('UNKNOWN', 'Unknown'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('BROTHER_SISTER', 'Brother / Sister'), ('COUSIN', 'Cousin'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('HEAD', 'Head of household (self)'), ('MOTHER_FATHER', 'Mother / Father'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('OTHER', 'Other'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband')], default='', max_length=255)),
                ('sex', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], max_length=255)),
                ('birth_date', models.DateField()),
                ('birth_doc', models.CharField(blank=True, max_length=128)),
                ('marital_status', models.CharField(choices=[('', 'None'), ('DIVORCED', 'Divorced'), ('MARRIED', 'Married'), ('SEPARATED', 'Separated'), ('SINGLE', 'Single'), ('WIDOWED', 'Widowed')], max_length=255)),
                ('disability', models.CharField(choices=[('disabled', 'disabled'), ('not disabled', 'not disabled')], default='not disabled', max_length=20)),
                ('iban', models.CharField(blank=True, default='', max_length=255)),
                ('bank_name', models.CharField(blank=True, default='', max_length=255)),
                ('household', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='individuals', to='registration_datahub.diiahousehold')),
                ('imported_individual', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diia_individuals', to='registration_datahub.importedindividual')),
                ('registration_data_import', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diia_individuals', to='registration_datahub.registrationdataimportdatahub')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='diiahousehold',
            name='head_of_household',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='registration_datahub.diiaindividual'),
        ),
        migrations.AddField(
            model_name='diiahousehold',
            name='imported_household',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diia_households', to='registration_datahub.importedhousehold'),
        ),
        migrations.AddField(
            model_name='diiahousehold',
            name='registration_data_import',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='diia_households', to='registration_datahub.registrationdataimportdatahub'),
        ),
    ]
