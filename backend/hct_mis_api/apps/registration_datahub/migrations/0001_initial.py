# Generated by Django 2.2.8 on 2019-12-16 10:05

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import phonenumber_field.modelfields
import sorl.thumbnail.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Household',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('household_ca_id', models.CharField(max_length=255)),
                ('consent', sorl.thumbnail.fields.ImageField(upload_to='')),
                ('residence_status', models.CharField(choices=[('REFUGEE', 'Refugee'), ('MIGRANT', 'Migrant'), ('CITIZEN', 'Citizen'), ('IDP', 'IDP'), ('OTHER', 'Other')], max_length=255)),
                ('nationality', models.CharField(choices=[('AF', 'Afghan'), ('AL', 'Albanian'), ('DZ', 'Algerian'), ('AD', 'Andorran'), ('AO', 'Angolan'), ('AR', 'Argentinian'), ('AM', 'Armenian'), ('A', 'Australian'), ('AT', 'Austrian'), ('AZ', 'Azerbaijani'), ('BS', 'Bahamian'), ('BH', 'Bahraini'), ('BD', 'Bangladeshi'), ('BB', 'Barbadian'), ('BY', 'Belorussian'), ('BE', 'Belgian'), ('BZ', 'Belizian'), ('BJ', 'Beninese'), ('BT', 'Bhutanese'), ('BO', 'Bolivian'), ('BA', 'Bosnian'), ('BW', 'Botswanan'), ('BR', 'Brazilian'), ('GB', 'British'), ('BN', 'Bruneian'), ('BG', 'Bulgarian'), ('BF', 'Burkinese'), ('MM', 'Burmese'), ('BF', 'Burundian'), ('BI', 'Cambodian'), ('CM', 'Cameroonian'), ('CA', 'Canadian'), ('CV', 'Cape Verdean'), ('TD', 'Chadian'), ('CL', 'Chilean'), ('CN', 'Chinese'), ('CO', 'Colombian'), ('CG', 'Congolese'), ('CR', 'Costa Rican'), ('HR', 'Croatian'), ('C', 'Cuban'), ('CY', 'Cypriot'), ('CZ', 'Czech'), ('DK', 'Danish'), ('DJ', 'Djiboutian'), ('DM', 'Dominican'), ('DO', 'Dominican'), ('EC', 'Ecuadorean'), ('EG', 'Egyptian'), ('SV', 'Salvadorean'), ('GB', 'English'), ('ER', 'Eritrean'), ('EE', 'Estonian'), ('ET', 'Ethiopian'), ('FJ', 'Fijian'), ('FI', 'Finnish'), ('FR', 'French'), ('GA', 'Gabonese'), ('GM', 'Gambian'), ('GE', 'Georgian'), ('DE', 'German'), ('GH', 'Ghanaian'), ('GR', 'Greek'), ('GD', 'Grenadian'), ('GT', 'Guatemalan'), ('GQ', 'Guinean'), ('GY', 'Guyanese'), ('HT', 'Haitian'), ('NL', 'Dutch'), ('HN', 'Honduran'), ('H', 'Hungarian'), ('IS', 'Icelandic'), ('IO', 'Indian'), ('ID', 'Indonesian'), ('IR', 'Iranian'), ('IQ', 'Iraqi'), ('IE', 'Irish'), ('IL', 'Israeli'), ('IT', 'Italian'), ('JM', 'Jamaican'), ('JP', 'Japanese'), ('JO', 'Jordanian'), ('KZ', 'Kazakh'), ('KE', 'Kenyan'), ('KW', 'Kuwaiti'), ('LA', 'Laotian'), ('LV', 'Latvian'), ('LB', 'Lebanese'), ('LR', 'Liberian'), ('LY', 'Libyan'), ('LT', 'Lithuanian'), ('MK', 'Macedonian'), ('MG', 'Malagasay'), ('MW', 'Malawian'), ('MY', 'Malaysian'), ('MV', 'Maldivian'), ('ML', 'Malian'), ('MT', 'Maltese'), ('MR', 'Mauritanian'), ('M', 'Mauritian'), ('MX', 'Mexican'), ('MD', 'Moldovan'), ('MC', 'Monacan'), ('MN', 'Mongolian'), ('ME', 'Montenegrin'), ('MA', 'Moroccan'), ('MZ', 'Mozambican'), ('NA', 'Namibian'), ('NP', 'Nepalese'), ('NI', 'Nicaraguan'), ('NE', 'Nigerien'), ('NG', 'Nigerian'), ('KP', 'North Korean'), ('NO', 'Norwegian'), ('OM', 'Omani'), ('PK', 'Pakistani'), ('PA', 'Panamanian'), ('PG', 'Guinean'), ('PY', 'Paraguayan'), ('PE', 'Peruvian'), ('PH', 'Philippine'), ('PL', 'Polish'), ('PT', 'Portuguese'), ('QA', 'Qatari'), ('RO', 'Romanian'), ('R', 'Russian'), ('RW', 'Rwandan'), ('SA', 'Saudi'), ('AE', 'Scottish'), ('SN', 'Senegalese'), ('RS', 'Serbian'), ('SC', 'Seychellois'), ('SL', 'Sierra Leonian'), ('SG', 'Singaporean'), ('SK', 'Slovak'), ('SI', 'Slovenian'), ('SO', 'Somali'), ('ZA', 'South African'), ('KR', 'South Korean'), ('ES', 'Spanish'), ('LK', 'Sri Lankan'), ('SD', 'Sudanese'), ('SR', 'Surinamese'), ('SZ', 'Swazi'), ('SE', 'Swedish'), ('CH', 'Swiss'), ('SY', 'Syrian'), ('TW', 'Taiwanese'), ('TJ', 'Tadjik'), ('TZ', 'Tanzanian'), ('TH', 'Thai'), ('TG', 'Togolese'), ('TT', 'Trinidadian'), ('TN', 'Tunisian'), ('TR', 'Turkish'), ('TM', 'Turkmen'), ('TV', 'Tuvaluan'), ('UG', 'Ugandan'), ('UA', 'Ukrainian'), ('UY', 'Uruguayan'), ('UZ', 'Uzbek'), ('V', 'Vanuatuan'), ('VE', 'Venezuelan'), ('VN', 'Vietnamese'), ('GB', 'Welsh'), ('YE', 'Yemeni'), ('ZM', 'Zambian'), ('ZW', 'Zimbabwean')], max_length=255)),
                ('family_size', models.PositiveIntegerField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RegistrationDataImport',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('IN_PROGRESS', 'In progress'), ('DONE', 'Done')], max_length=255)),
                ('import_date', models.DateTimeField()),
                ('imported_by', models.CharField(max_length=255)),
                ('data_source', models.CharField(choices=[('XLS', 'Excel'), ('3RD_PARTY', '3rd party'), ('XML', 'XML'), ('OTHER', 'Other')], max_length=255)),
                ('number_of_individuals', models.PositiveIntegerField()),
                ('number_of_households', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('individual_ca_id', models.CharField(max_length=255)),
                ('full_name', models.CharField(max_length=255)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('middle_name', models.CharField(max_length=255)),
                ('sex', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], max_length=255)),
                ('dob', models.DateField(blank=True, null=True)),
                ('estimated_dob', models.DateField(blank=True, null=True)),
                ('nationality', models.CharField(choices=[('AF', 'Afghan'), ('AL', 'Albanian'), ('DZ', 'Algerian'), ('AD', 'Andorran'), ('AO', 'Angolan'), ('AR', 'Argentinian'), ('AM', 'Armenian'), ('A', 'Australian'), ('AT', 'Austrian'), ('AZ', 'Azerbaijani'), ('BS', 'Bahamian'), ('BH', 'Bahraini'), ('BD', 'Bangladeshi'), ('BB', 'Barbadian'), ('BY', 'Belorussian'), ('BE', 'Belgian'), ('BZ', 'Belizian'), ('BJ', 'Beninese'), ('BT', 'Bhutanese'), ('BO', 'Bolivian'), ('BA', 'Bosnian'), ('BW', 'Botswanan'), ('BR', 'Brazilian'), ('GB', 'British'), ('BN', 'Bruneian'), ('BG', 'Bulgarian'), ('BF', 'Burkinese'), ('MM', 'Burmese'), ('BF', 'Burundian'), ('BI', 'Cambodian'), ('CM', 'Cameroonian'), ('CA', 'Canadian'), ('CV', 'Cape Verdean'), ('TD', 'Chadian'), ('CL', 'Chilean'), ('CN', 'Chinese'), ('CO', 'Colombian'), ('CG', 'Congolese'), ('CR', 'Costa Rican'), ('HR', 'Croatian'), ('C', 'Cuban'), ('CY', 'Cypriot'), ('CZ', 'Czech'), ('DK', 'Danish'), ('DJ', 'Djiboutian'), ('DM', 'Dominican'), ('DO', 'Dominican'), ('EC', 'Ecuadorean'), ('EG', 'Egyptian'), ('SV', 'Salvadorean'), ('GB', 'English'), ('ER', 'Eritrean'), ('EE', 'Estonian'), ('ET', 'Ethiopian'), ('FJ', 'Fijian'), ('FI', 'Finnish'), ('FR', 'French'), ('GA', 'Gabonese'), ('GM', 'Gambian'), ('GE', 'Georgian'), ('DE', 'German'), ('GH', 'Ghanaian'), ('GR', 'Greek'), ('GD', 'Grenadian'), ('GT', 'Guatemalan'), ('GQ', 'Guinean'), ('GY', 'Guyanese'), ('HT', 'Haitian'), ('NL', 'Dutch'), ('HN', 'Honduran'), ('H', 'Hungarian'), ('IS', 'Icelandic'), ('IO', 'Indian'), ('ID', 'Indonesian'), ('IR', 'Iranian'), ('IQ', 'Iraqi'), ('IE', 'Irish'), ('IL', 'Israeli'), ('IT', 'Italian'), ('JM', 'Jamaican'), ('JP', 'Japanese'), ('JO', 'Jordanian'), ('KZ', 'Kazakh'), ('KE', 'Kenyan'), ('KW', 'Kuwaiti'), ('LA', 'Laotian'), ('LV', 'Latvian'), ('LB', 'Lebanese'), ('LR', 'Liberian'), ('LY', 'Libyan'), ('LT', 'Lithuanian'), ('MK', 'Macedonian'), ('MG', 'Malagasay'), ('MW', 'Malawian'), ('MY', 'Malaysian'), ('MV', 'Maldivian'), ('ML', 'Malian'), ('MT', 'Maltese'), ('MR', 'Mauritanian'), ('M', 'Mauritian'), ('MX', 'Mexican'), ('MD', 'Moldovan'), ('MC', 'Monacan'), ('MN', 'Mongolian'), ('ME', 'Montenegrin'), ('MA', 'Moroccan'), ('MZ', 'Mozambican'), ('NA', 'Namibian'), ('NP', 'Nepalese'), ('NI', 'Nicaraguan'), ('NE', 'Nigerien'), ('NG', 'Nigerian'), ('KP', 'North Korean'), ('NO', 'Norwegian'), ('OM', 'Omani'), ('PK', 'Pakistani'), ('PA', 'Panamanian'), ('PG', 'Guinean'), ('PY', 'Paraguayan'), ('PE', 'Peruvian'), ('PH', 'Philippine'), ('PL', 'Polish'), ('PT', 'Portuguese'), ('QA', 'Qatari'), ('RO', 'Romanian'), ('R', 'Russian'), ('RW', 'Rwandan'), ('SA', 'Saudi'), ('AE', 'Scottish'), ('SN', 'Senegalese'), ('RS', 'Serbian'), ('SC', 'Seychellois'), ('SL', 'Sierra Leonian'), ('SG', 'Singaporean'), ('SK', 'Slovak'), ('SI', 'Slovenian'), ('SO', 'Somali'), ('ZA', 'South African'), ('KR', 'South Korean'), ('ES', 'Spanish'), ('LK', 'Sri Lankan'), ('SD', 'Sudanese'), ('SR', 'Surinamese'), ('SZ', 'Swazi'), ('SE', 'Swedish'), ('CH', 'Swiss'), ('SY', 'Syrian'), ('TW', 'Taiwanese'), ('TJ', 'Tadjik'), ('TZ', 'Tanzanian'), ('TH', 'Thai'), ('TG', 'Togolese'), ('TT', 'Trinidadian'), ('TN', 'Tunisian'), ('TR', 'Turkish'), ('TM', 'Turkmen'), ('TV', 'Tuvaluan'), ('UG', 'Ugandan'), ('UA', 'Ukrainian'), ('UY', 'Uruguayan'), ('UZ', 'Uzbek'), ('V', 'Vanuatuan'), ('VE', 'Venezuelan'), ('VN', 'Vietnamese'), ('GB', 'Welsh'), ('YE', 'Yemeni'), ('ZM', 'Zambian'), ('ZW', 'Zimbabwean')], max_length=255)),
                ('martial_status', models.CharField(choices=[('SINGLE', 'SINGLE'), ('MARRIED', 'Married'), ('WIDOW', 'Widow'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated')], max_length=255)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('identification_type', models.CharField(choices=[('NA', 'N/A'), ('BIRTH_CERTIFICATE', 'Birth Certificate'), ('DRIVING_LICENSE', 'Driving License'), ('UNHCR_ID_CARD', 'UNHCR ID card'), ('NATIONAL_ID', 'National ID'), ('NATIONAL_PASSPORT', 'National Passport')], max_length=255)),
                ('identification_number', models.CharField(max_length=255)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individuals', to='registration_datahub.Household')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='household',
            name='registration_data_import_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='households', to='registration_datahub.RegistrationDataImport'),
        ),
    ]
