# Generated by Django 2.2.16 on 2021-04-15 20:18

import concurrency.fields
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.citext
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import model_utils.fields
import multiselectfield.db.fields
import phonenumber_field.modelfields
import sorl.thumbnail.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_migration'),
        ('registration_data', '0001_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('WFP', 'WFP'), ('UNHCR', 'UNHCR')], max_length=100)),
                ('label', models.CharField(max_length=100)),
                ('country', django_countries.fields.CountryField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('is_removed', models.BooleanField(default=False)),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('document_number', models.CharField(blank=True, max_length=255)),
                ('photo', models.ImageField(blank=True, upload_to='')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('VALID', 'Valid'), ('NEED_INVESTIGATION', 'Need Investigation'), ('INVALID', 'Invalid')], default='PENDING', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('label', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('BIRTH_CERTIFICATE', 'Birth Certificate'), ('DRIVERS_LICENSE', "Driver's License"), ('NATIONAL_ID', 'National ID'), ('NATIONAL_PASSPORT', 'National Passport'), ('ELECTORAL_CARD', 'Electoral Card'), ('OTHER', 'Other')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentValidator',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('regex', models.CharField(default='.*', max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EntitlementCard',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('card_number', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('ERRONEOUS', 'Erroneous'), ('CLOSED', 'Closed')], default='ACTIVE', max_length=10)),
                ('card_type', models.CharField(max_length=255)),
                ('current_card_size', models.CharField(max_length=255)),
                ('card_custodian', models.CharField(max_length=255)),
                ('service_provider', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Household',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('is_removed', models.BooleanField(default=False)),
                ('removed_date', models.DateTimeField(blank=True, null=True)),
                ('last_sync_at', models.DateTimeField(blank=True, null=True)),
                ('version', concurrency.fields.IntegerVersionField(default=0, help_text='record revision number')),
                ('withdrawn', models.BooleanField(db_index=True, default=False)),
                ('withdrawn_date', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('consent_sign', sorl.thumbnail.fields.ImageField(blank=True, upload_to='', validators=[django.core.validators.validate_image_file_extension])),
                ('consent', models.NullBooleanField()),
                ('consent_sharing', multiselectfield.db.fields.MultiSelectField(choices=[('', 'None'), ('UNICEF', 'UNICEF'), ('HUMANITARIAN_PARTNER', 'Humanitarian partners'), ('PRIVATE_PARTNER', 'Private partners'), ('GOVERNMENT_PARTNER', 'Government partners')], default='', max_length=63)),
                ('residence_status', models.CharField(choices=[('', 'None'), ('IDP', 'Displaced  |  Internally Displaced People'), ('REFUGEE', 'Displaced  |  Refugee / Asylum Seeker'), ('OTHERS_OF_CONCERN', 'Displaced  |  Others of Concern'), ('HOST', 'Non-displaced  |   Host'), ('NON_HOST', 'Non-displaced  |   Non-host')], max_length=255)),
                ('country_origin', django_countries.fields.CountryField(blank=True, db_index=True, max_length=2)),
                ('country', django_countries.fields.CountryField(db_index=True, max_length=2)),
                ('size', models.PositiveIntegerField(db_index=True)),
                ('address', django.contrib.postgres.fields.citext.CICharField(blank=True, max_length=255)),
                ('geopoint', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('female_age_group_0_5_count', models.PositiveIntegerField(default=None, null=True)),
                ('female_age_group_6_11_count', models.PositiveIntegerField(default=None, null=True)),
                ('female_age_group_12_17_count', models.PositiveIntegerField(default=None, null=True)),
                ('female_age_group_18_59_count', models.PositiveIntegerField(default=None, null=True)),
                ('female_age_group_60_count', models.PositiveIntegerField(default=None, null=True)),
                ('pregnant_count', models.PositiveIntegerField(default=None, null=True)),
                ('male_age_group_0_5_count', models.PositiveIntegerField(default=None, null=True)),
                ('male_age_group_6_11_count', models.PositiveIntegerField(default=None, null=True)),
                ('male_age_group_12_17_count', models.PositiveIntegerField(default=None, null=True)),
                ('male_age_group_18_59_count', models.PositiveIntegerField(default=None, null=True)),
                ('male_age_group_60_count', models.PositiveIntegerField(default=None, null=True)),
                ('female_age_group_0_5_disabled_count', models.PositiveIntegerField(default=None, null=True)),
                ('female_age_group_6_11_disabled_count', models.PositiveIntegerField(default=None, null=True)),
                ('female_age_group_12_17_disabled_count', models.PositiveIntegerField(default=None, null=True)),
                ('female_age_group_18_59_disabled_count', models.PositiveIntegerField(default=None, null=True)),
                ('female_age_group_60_disabled_count', models.PositiveIntegerField(default=None, null=True)),
                ('male_age_group_0_5_disabled_count', models.PositiveIntegerField(default=None, null=True)),
                ('male_age_group_6_11_disabled_count', models.PositiveIntegerField(default=None, null=True)),
                ('male_age_group_12_17_disabled_count', models.PositiveIntegerField(default=None, null=True)),
                ('male_age_group_18_59_disabled_count', models.PositiveIntegerField(default=None, null=True)),
                ('male_age_group_60_disabled_count', models.PositiveIntegerField(default=None, null=True)),
                ('returnee', models.NullBooleanField()),
                ('flex_fields', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('first_registration_date', models.DateTimeField()),
                ('last_registration_date', models.DateTimeField()),
                ('fchild_hoh', models.NullBooleanField()),
                ('child_hoh', models.NullBooleanField()),
                ('unicef_id', django.contrib.postgres.fields.citext.CICharField(blank=True, db_index=True, default='', max_length=250)),
                ('start', models.DateTimeField(blank=True, null=True)),
                ('deviceid', models.CharField(blank=True, default='', max_length=250)),
                ('name_enumerator', models.CharField(blank=True, default='', max_length=250)),
                ('org_enumerator', models.CharField(choices=[('', 'None'), ('UNICEF', 'UNICEF'), ('PARTNER', 'Partner')], default='', max_length=250)),
                ('org_name_enumerator', models.CharField(blank=True, default='', max_length=250)),
                ('village', models.CharField(blank=True, default='', max_length=250)),
                ('registration_method', models.CharField(choices=[('', 'None'), ('HH_REGISTRATION', 'Household Registration'), ('COMMUNITY', 'Community-level Registration')], default='', max_length=250)),
                ('collect_individual_data', models.CharField(choices=[('', 'None'), ('1', 'Yes'), ('0', 'No')], default='', max_length=250)),
                ('currency', models.CharField(choices=[('', 'None'), ('AED', 'United Arab Emirates dirham'), ('AFN', 'Afghan afghani'), ('ALL', 'Albanian lek'), ('AMD', 'Armenian dram'), ('ANG', 'Netherlands Antillean guilder'), ('AOA', 'Angolan kwanza'), ('ARS', 'Argentine peso'), ('AUD', 'Australian dollar'), ('AWG', 'Aruban florin'), ('AZN', 'Azerbaijani manat'), ('BAM', 'Bosnia and Herzegovina convertible mark'), ('BBD', 'Barbados dollar'), ('BDT', 'Bangladeshi taka'), ('BGN', 'Bulgarian lev'), ('BHD', 'Bahraini dinar'), ('BIF', 'Burundian franc'), ('BMD', 'Bermudian dollar'), ('BND', 'Brunei dollar'), ('BOB', 'Boliviano'), ('BOV', 'Bolivian Mvdol (funds code)'), ('BRL', 'Brazilian real'), ('BSD', 'Bahamian dollar'), ('BTN', 'Bhutanese ngultrum'), ('BWP', 'Botswana pula'), ('BYN', 'Belarusian ruble'), ('BZD', 'Belize dollar'), ('CAD', 'Canadian dollar'), ('CDF', 'Congolese franc'), ('CHF', 'Swiss franc'), ('CLP', 'Chilean peso'), ('CNY', 'Chinese yuan'), ('COP', 'Colombian peso'), ('CRC', 'Costa Rican colon'), ('CUC', 'Cuban convertible peso'), ('CUP', 'Cuban peso'), ('CVE', 'Cape Verdean escudo'), ('CZK', 'Czech koruna'), ('DJF', 'Djiboutian franc'), ('DKK', 'Danish krone'), ('DOP', 'Dominican peso'), ('DZD', 'Algerian dinar'), ('EGP', 'Egyptian pound'), ('ERN', 'Eritrean nakfa'), ('ETB', 'Ethiopian birr'), ('EUR', 'Euro'), ('FJD', 'Fiji dollar'), ('FKP', 'Falkland Islands pound'), ('GBP', 'Pound sterling'), ('GEL', 'Georgian lari'), ('GHS', 'Ghanaian cedi'), ('GIP', 'Gibraltar pound'), ('GMD', 'Gambian dalasi'), ('GNF', 'Guinean franc'), ('GTQ', 'Guatemalan quetzal'), ('GYD', 'Guyanese dollar'), ('HKD', 'Hong Kong dollar'), ('HNL', 'Honduran lempira'), ('HRK', 'Croatian kuna'), ('HTG', 'Haitian gourde'), ('HUF', 'Hungarian forint'), ('IDR', 'Indonesian rupiah'), ('ILS', 'Israeli new shekel'), ('INR', 'Indian rupee'), ('IQD', 'Iraqi dinar'), ('IRR', 'Iranian rial'), ('ISK', 'Icelandic króna'), ('JMD', 'Jamaican dollar'), ('JOD', 'Jordanian dinar'), ('JPY', 'Japanese yen'), ('KES', 'Kenyan shilling'), ('KGS', 'Kyrgyzstani som'), ('KHR', 'Cambodian riel'), ('KMF', 'Comoro franc'), ('KPW', 'North Korean won'), ('KRW', 'South Korean won'), ('KWD', 'Kuwaiti dinar'), ('KYD', 'Cayman Islands dollar'), ('KZT', 'Kazakhstani tenge'), ('LAK', 'Lao kip'), ('LBP', 'Lebanese pound'), ('LKR', 'Sri Lankan rupee'), ('LRD', 'Liberian dollar'), ('LSL', 'Lesotho loti'), ('LYD', 'Libyan dinar'), ('MAD', 'Moroccan dirham'), ('MDL', 'Moldovan leu'), ('MGA', 'Malagasy ariary'), ('MKD', 'Macedonian denar'), ('MMK', 'Myanmar kyat'), ('MNT', 'Mongolian tögrög'), ('MOP', 'Macanese pataca'), ('MRU', 'Mauritanian ouguiya'), ('MUR', 'Mauritian rupee'), ('MVR', 'Maldivian rufiyaa'), ('MWK', 'Malawian kwacha'), ('MXN', 'Mexican peso'), ('MYR', 'Malaysian ringgit'), ('MZN', 'Mozambican metical'), ('NAD', 'Namibian dollar'), ('NGN', 'Nigerian naira'), ('NIO', 'Nicaraguan córdoba'), ('NOK', 'Norwegian krone'), ('NPR', 'Nepalese rupee'), ('NZD', 'New Zealand dollar'), ('OMR', 'Omani rial'), ('PAB', 'Panamanian balboa'), ('PEN', 'Peruvian sol'), ('PGK', 'Papua New Guinean kina'), ('PHP', 'Philippine peso'), ('PKR', 'Pakistani rupee'), ('PLN', 'Polish złoty'), ('PYG', 'Paraguayan guaraní'), ('QAR', 'Qatari riyal'), ('RON', 'Romanian leu'), ('RSD', 'Serbian dinar'), ('RUB', 'Russian ruble'), ('RWF', 'Rwandan franc'), ('SAR', 'Saudi riyal'), ('SBD', 'Solomon Islands dollar'), ('SCR', 'Seychelles rupee'), ('SDG', 'Sudanese pound'), ('SEK', 'Swedish krona/kronor'), ('SGD', 'Singapore dollar'), ('SHP', 'Saint Helena pound'), ('SLL', 'Sierra Leonean leone'), ('SOS', 'Somali shilling'), ('SRD', 'Surinamese dollar'), ('SSP', 'South Sudanese pound'), ('STN', 'São Tomé and Príncipe dobra'), ('SVC', 'Salvadoran colón'), ('SYP', 'Syrian pound'), ('SZL', 'Swazi lilangeni'), ('THB', 'Thai baht'), ('TJS', 'Tajikistani somoni'), ('TMT', 'Turkmenistan manat'), ('TND', 'Tunisian dinar'), ('TOP', 'Tongan paʻanga'), ('TRY', 'Turkish lira'), ('TTD', 'Trinidad and Tobago dollar'), ('TWD', 'New Taiwan dollar'), ('TZS', 'Tanzanian shilling'), ('UAH', 'Ukrainian hryvnia'), ('UGX', 'Ugandan shilling'), ('USD', 'United States dollar'), ('UYU', 'Uruguayan peso'), ('UYW', 'Unidad previsional[14]'), ('UZS', 'Uzbekistan som'), ('VES', 'Venezuelan bolívar soberano'), ('VND', 'Vietnamese đồng'), ('VUV', 'Vanuatu vatu'), ('WST', 'Samoan tala'), ('XAF', 'CFA franc BEAC'), ('XAG', 'Silver (one troy ounce)'), ('XAU', 'Gold (one troy ounce)'), ('XCD', 'East Caribbean dollar'), ('XOF', 'CFA franc BCEAO'), ('XPF', 'CFP franc (franc Pacifique)'), ('YER', 'Yemeni rial'), ('ZAR', 'South African rand'), ('ZMW', 'Zambian kwacha'), ('ZWL', 'Zimbabwean dollar')], default='', max_length=250)),
                ('unhcr_id', models.CharField(blank=True, db_index=True, default='', max_length=250)),
                ('admin_area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.AdminArea')),
                ('business_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.BusinessArea')),
            ],
            options={
                'verbose_name': 'Household',
            },
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('is_removed', models.BooleanField(default=False)),
                ('removed_date', models.DateTimeField(blank=True, null=True)),
                ('last_sync_at', models.DateTimeField(blank=True, null=True)),
                ('version', concurrency.fields.IntegerVersionField(default=0, help_text='record revision number')),
                ('duplicate', models.BooleanField(db_index=True, default=False)),
                ('duplicate_date', models.DateTimeField(blank=True, null=True)),
                ('withdrawn', models.BooleanField(db_index=True, default=False)),
                ('withdrawn_date', models.DateTimeField(blank=True, null=True)),
                ('individual_id', models.CharField(blank=True, max_length=255)),
                ('photo', models.ImageField(blank=True, upload_to='')),
                ('full_name', django.contrib.postgres.fields.citext.CICharField(db_index=True, max_length=255, validators=[django.core.validators.MinLengthValidator(2)])),
                ('given_name', django.contrib.postgres.fields.citext.CICharField(blank=True, db_index=True, max_length=85)),
                ('middle_name', django.contrib.postgres.fields.citext.CICharField(blank=True, db_index=True, max_length=85)),
                ('family_name', django.contrib.postgres.fields.citext.CICharField(blank=True, db_index=True, max_length=85)),
                ('sex', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], db_index=True, max_length=255)),
                ('birth_date', models.DateField(db_index=True)),
                ('estimated_birth_date', models.BooleanField(default=False)),
                ('marital_status', models.CharField(choices=[('', 'None'), ('SINGLE', 'Single'), ('MARRIED', 'Married'), ('WIDOWED', 'Widowed'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated')], db_index=True, default='', max_length=255)),
                ('phone_no', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('phone_no_alternative', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('relationship', models.CharField(blank=True, choices=[('UNKNOWN', 'Unknown'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('HEAD', 'Head of household (self)'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('BROTHER_SISTER', 'Brother / Sister'), ('MOTHER_FATHER', 'Mother / Father'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('COUSIN', 'Cousin')], help_text='This represents the MEMBER relationship. can be blank\n            as well if household is null!', max_length=255)),
                ('disability', models.BooleanField(default=False)),
                ('work_status', models.CharField(blank=True, choices=[('1', 'Yes'), ('0', 'No'), ('NOT_PROVIDED', 'Not provided')], default='NOT_PROVIDED', max_length=20)),
                ('first_registration_date', models.DateField()),
                ('last_registration_date', models.DateField()),
                ('flex_fields', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('enrolled_in_nutrition_programme', models.NullBooleanField()),
                ('administration_of_rutf', models.NullBooleanField()),
                ('unicef_id', django.contrib.postgres.fields.citext.CICharField(blank=True, db_index=True, max_length=250)),
                ('deduplication_golden_record_status', models.CharField(choices=[('UNIQUE', 'Unique'), ('DUPLICATE', 'Duplicate'), ('NEEDS_ADJUDICATION', 'Needs Adjudication'), ('NOT_PROCESSED', 'Not Processed')], default='UNIQUE', max_length=50)),
                ('deduplication_batch_status', models.CharField(choices=[('SIMILAR_IN_BATCH', 'Similar in batch'), ('DUPLICATE_IN_BATCH', 'Duplicate in batch'), ('UNIQUE_IN_BATCH', 'Unique in batch'), ('NOT_PROCESSED', 'Not Processed')], default='UNIQUE_IN_BATCH', max_length=50)),
                ('deduplication_golden_record_results', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('deduplication_batch_results', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('imported_individual_id', models.UUIDField(null=True)),
                ('sanction_list_possible_match', models.BooleanField(default=False)),
                ('sanction_list_confirmed_match', models.BooleanField(default=False)),
                ('sanction_list_last_check', models.DateTimeField(blank=True, null=True)),
                ('pregnant', models.NullBooleanField()),
                ('observed_disability', multiselectfield.db.fields.MultiSelectField(choices=[('NONE', 'None'), ('SEEING', 'Difficulty seeing (even if wearing glasses)'), ('HEARING', 'Difficulty hearing (even if using a hearing aid)'), ('WALKING', 'Difficulty walking or climbing steps'), ('MEMORY', 'Difficulty remembering or concentrating'), ('SELF_CARE', 'Difficulty with self care (washing, dressing)'), ('COMMUNICATING', 'Difficulty communicating (e.g understanding or being understood)')], default='NONE', max_length=58)),
                ('seeing_disability', models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'), ('LOT_DIFFICULTY', 'A lot of difficulty'), ('CANNOT_DO', 'Cannot do at all')], max_length=50)),
                ('hearing_disability', models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'), ('LOT_DIFFICULTY', 'A lot of difficulty'), ('CANNOT_DO', 'Cannot do at all')], max_length=50)),
                ('physical_disability', models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'), ('LOT_DIFFICULTY', 'A lot of difficulty'), ('CANNOT_DO', 'Cannot do at all')], max_length=50)),
                ('memory_disability', models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'), ('LOT_DIFFICULTY', 'A lot of difficulty'), ('CANNOT_DO', 'Cannot do at all')], max_length=50)),
                ('selfcare_disability', models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'), ('LOT_DIFFICULTY', 'A lot of difficulty'), ('CANNOT_DO', 'Cannot do at all')], max_length=50)),
                ('comms_disability', models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'), ('LOT_DIFFICULTY', 'A lot of difficulty'), ('CANNOT_DO', 'Cannot do at all')], max_length=50)),
                ('who_answers_phone', models.CharField(blank=True, max_length=150)),
                ('who_answers_alt_phone', models.CharField(blank=True, max_length=150)),
                ('business_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.BusinessArea')),
                ('household', models.ForeignKey(blank=True, help_text='This represents the household this person is a MEMBER,\n            and if null then relationship is NON_BENEFICIARY and that\n            simply means they are a representative of one or more households\n            and not a member of one.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='individuals', to='household.Household')),
                ('registration_data_import', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='individuals', to='registration_data.RegistrationDataImport')),
            ],
            options={
                'verbose_name': 'Individual',
            },
        ),
        migrations.CreateModel(
            name='IndividualRoleInHousehold',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('last_sync_at', models.DateTimeField(blank=True, null=True)),
                ('role', models.CharField(blank=True, choices=[('PRIMARY', 'Primary collector'), ('ALTERNATE', 'Alternate collector'), ('NO_ROLE', 'None')], max_length=255)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individuals_and_roles', to='household.Household')),
                ('individual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='households_and_roles', to='household.Individual')),
            ],
        ),
        migrations.CreateModel(
            name='IndividualIdentity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=255)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individual_identities', to='household.Agency')),
                ('individual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identities', to='household.Individual')),
            ],
        ),
        migrations.AddField(
            model_name='household',
            name='head_of_household',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='heading_household', to='household.Individual'),
        ),
    ]
