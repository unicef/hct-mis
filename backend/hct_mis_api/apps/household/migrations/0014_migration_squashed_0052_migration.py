# Generated by Django 3.2.12 on 2022-03-18 10:27

import concurrency.fields
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django_countries.fields
import model_utils.fields
import multiselectfield.db.fields
import sorl.thumbnail.fields
import uuid


class Migration(migrations.Migration):

    replaces = [('household', '0014_migration'), ('household', '0015_migration'), ('household', '0016_migration'), ('household', '0017_migration'), ('household', '0018_migration'), ('household', '0019_migration'), ('household', '0020_migration'), ('household', '0021_migration'), ('household', '0022_migration'), ('household', '0023_migration'), ('household', '0024_migration'), ('household', '0025_migration'), ('household', '0026_migration'), ('household', '0027_migration'), ('household', '0028_migration'), ('household', '0029_migration'), ('household', '0030_migration'), ('household', '0031_migration'), ('household', '0032_migration'), ('household', '0033_migration'), ('household', '0034_migration'), ('household', '0035_migration'), ('household', '0036_migration'), ('household', '0037_migration'), ('household', '0038_migration'), ('household', '0039_migration'), ('household', '0040_migration'), ('household', '0041_migration'), ('household', '0042_migration'), ('household', '0043_migration'), ('household', '0044_migration'), ('household', '0045_migration'), ('household', '0046_migration'), ('household', '0047_migration'), ('household', '0048_migration'), ('household', '0049_migration'), ('household', '0050_migration'), ('household', '0051_migration'), ('household', '0052_migration')]

    dependencies = [
        ('core', '0004_migration'),
        ('core', '0001_migration'),
        ('household', '0013_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='individual',
            name='role',
        ),
        migrations.AlterField(
            model_name='individual',
            name='household',
            field=models.ForeignKey(blank=True, help_text='This represents the household this person is a MEMBER,\n            and if null then relationship is NON_BENEFICIARY and that\n            simply means they are a representative of one or more households\n            and not a member of one.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='individuals', to='household.household'),
        ),
        migrations.AlterUniqueTogether(
            name='document',
            unique_together=set(),
        ),
        migrations.CreateModel(
            name='IndividualRoleInHousehold',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_sync_at', models.DateTimeField(null=True)),
                ('role', models.CharField(blank=True, choices=[('PRIMARY', 'Primary collector'), ('ALTERNATE', 'Alternate collector'), ('NO_ROLE', 'None')], max_length=255)),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individuals_and_roles', to='household.household')),
                ('individual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='households_and_roles', to='household.individual')),
            ],
            options={
                'unique_together': {('role', 'household')},
            },
        ),
        migrations.AddField(
            model_name='household',
            name='representatives',
            field=models.ManyToManyField(help_text='This is only used to track collector (primary or secondary) of a household.\n            They may still be a HOH of this household or any other household.\n            Through model will contain the role (ROLE_CHOICE) they are connected with on.', related_name='represented_households', through='household.IndividualRoleInHousehold', to='household.Individual'),
        ),
        migrations.AddField(
            model_name='household',
            name='business_area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.businessarea'),
        ),
        migrations.AlterUniqueTogether(
            name='individualidentity',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='individual',
            name='sanction_list_possible_match',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='individual',
            name='pregnant',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='deduplication_golden_record_results',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='individual',
            name='deduplication_golden_record_status',
            field=models.CharField(choices=[('UNIQUE', 'Unique'), ('DUPLICATE', 'Duplicate'), ('NEEDS_ADJUDICATION', 'Needs Adjudication'), ('NOT_PROCESSED', 'Not Processed')], default='UNIQUE', max_length=50),
        ),
        migrations.AddField(
            model_name='individual',
            name='deduplication_batch_results',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='individual',
            name='deduplication_batch_status',
            field=models.CharField(choices=[('SIMILAR_IN_BATCH', 'Similar in batch'), ('DUPLICATE_IN_BATCH', 'Duplicate in batch'), ('UNIQUE_IN_BATCH', 'Unique in batch'), ('NOT_PROCESSED', 'Not Processed')], default='UNIQUE_IN_BATCH', max_length=50),
        ),
        migrations.AddField(
            model_name='individual',
            name='imported_individual_id',
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='sanction_list_last_check',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='household',
            name='consent',
        ),
        migrations.AddField(
            model_name='household',
            name='child_hoh',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='consent_sharing',
            field=multiselectfield.db.fields.MultiSelectField(
                choices=[('', 'None'), ('UNICEF', 'UNICEF'), ('HUMANITARIAN_PARTNER', 'Humanitarian partners'),
                         ('PRIVATE_PARTNER', 'Private partners'), ('GOVERNMENT_PARTNER', 'Government partners')],
                default='', max_length=63),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='household',
            name='consent_sign',
            field=sorl.thumbnail.fields.ImageField(blank=True, upload_to='', validators=[django.core.validators.validate_image_file_extension]),
        ),
        migrations.AddField(
            model_name='household',
            name='deviceid',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='household',
            name='end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='fchild_hoh',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='name_enumerator',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='household',
            name='org_enumerator',
            field=models.CharField(choices=[('', 'None'), ('UNICEF', 'UNICEF'), ('PARTNER', 'Partner')], default='',
                                   max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='household',
            name='org_name_enumerator',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='household',
            name='start',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='village',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='individual',
            name='comms_disability',
            field=models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'), ('LOT_DIFFICULTY', 'A lot of difficulty'), ('CANNOT_DO', 'Cannot do at all')], max_length=50),
        ),
        migrations.AddField(
            model_name='individual',
            name='hearing_disability',
            field=models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'),
                                                        ('LOT_DIFFICULTY', 'A lot of difficulty'),
                                                        ('CANNOT_DO', 'Cannot do at all')], max_length=50),
        ),
        migrations.AddField(
            model_name='individual',
            name='memory_disability',
            field=models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'),
                                                        ('LOT_DIFFICULTY', 'A lot of difficulty'),
                                                        ('CANNOT_DO', 'Cannot do at all')], max_length=50),
        ),
        migrations.AddField(
            model_name='individual',
            name='observed_disability',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('NONE', 'None'), ('SEEING', 'Difficulty seeing (even if wearing glasses)'), ('HEARING', 'Difficulty hearing (even if using a hearing aid)'), ('WALKING', 'Difficulty walking or climbing steps'), ('MEMORY', 'Difficulty remembering or concentrating'), ('SELF_CARE', 'Difficulty with self care (washing, dressing)'), ('COMMUNICATING', 'Difficulty communicating (e.g understanding or being understood)')], default='NONE', max_length=58),
        ),
        migrations.AddField(
            model_name='individual',
            name='physical_disability',
            field=models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'),
                                                        ('LOT_DIFFICULTY', 'A lot of difficulty'),
                                                        ('CANNOT_DO', 'Cannot do at all')], max_length=50),
        ),
        migrations.AddField(
            model_name='individual',
            name='seeing_disability',
            field=models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'),
                                                        ('LOT_DIFFICULTY', 'A lot of difficulty'),
                                                        ('CANNOT_DO', 'Cannot do at all')], max_length=50),
        ),
        migrations.AddField(
            model_name='individual',
            name='selfcare_disability',
            field=models.CharField(blank=True, choices=[('', 'None'), ('SOME_DIFFICULTY', 'Some difficulty'),
                                                        ('LOT_DIFFICULTY', 'A lot of difficulty'),
                                                        ('CANNOT_DO', 'Cannot do at all')], max_length=50),
        ),
        migrations.AddField(
            model_name='individual',
            name='who_answers_alt_phone',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='individual',
            name='who_answers_phone',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name='household',
            name='residence_status',
            field=models.CharField(choices=[('', 'None'), ('IDP', 'Displaced  |  Internally Displaced People'),
                                            ('REFUGEE', 'Displaced  |  Refugee / Asylum Seeker'),
                                            ('OTHERS_OF_CONCERN', 'Displaced  |  Others of Concern'),
                                            ('HOST', 'Non-displaced  |   Host'),
                                            ('NON_HOST', 'Non-displaced  |   Non-host')], max_length=255),
        ),
        migrations.AddField(
            model_name='household',
            name='consent',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='registration_data_import',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='individuals', to='registration_data.registrationdataimport'),
        ),
        migrations.AddField(
            model_name='document',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name='document',
            constraint=models.UniqueConstraint(condition=models.Q(('is_removed', False)), fields=('document_number', 'type'), name='unique_if_not_removed'),
        ),
        migrations.AlterField(
            model_name='individual',
            name='relationship',
            field=models.CharField(blank=True, choices=[('UNKNOWN', 'Unknown'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('HEAD', 'Head of household (self)'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('BROTHER_SISTER', 'Brother / Sister'), ('MOTHER_FATHER', 'Mother / Father'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('COUSIN', 'Cousin')], help_text='This represents the MEMBER relationship. can be blank\n            as well if household is null!', max_length=255),
        ),
        migrations.AddField(
            model_name='individual',
            name='business_area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.businessarea'),
        ),
        migrations.AlterModelManagers(
            name='individual',
            managers=[
                ('active_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='individual',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelManagers(
            name='individual',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='household',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveField(
            model_name='household',
            name='end',
        ),
        migrations.RemoveField(
            model_name='household',
            name='female_adults_count',
        ),
        migrations.RemoveField(
            model_name='household',
            name='female_adults_disabled_count',
        ),
        migrations.RemoveField(
            model_name='household',
            name='male_adults_count',
        ),
        migrations.RemoveField(
            model_name='household',
            name='male_adults_disabled_count',
        ),
        migrations.AddField(
            model_name='agency',
            name='country',
            field=django_countries.fields.CountryField(default='AF', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='household',
            name='currency',
            field=models.CharField(choices=[('', 'None'), ('AED', 'United Arab Emirates dirham'), ('AFN', 'Afghan afghani'), ('ALL', 'Albanian lek'), ('AMD', 'Armenian dram'), ('ANG', 'Netherlands Antillean guilder'), ('AOA', 'Angolan kwanza'), ('ARS', 'Argentine peso'), ('AUD', 'Australian dollar'), ('AWG', 'Aruban florin'), ('AZN', 'Azerbaijani manat'), ('BAM', 'Bosnia and Herzegovina convertible mark'), ('BBD', 'Barbados dollar'), ('BDT', 'Bangladeshi taka'), ('BGN', 'Bulgarian lev'), ('BHD', 'Bahraini dinar'), ('BIF', 'Burundian franc'), ('BMD', 'Bermudian dollar'), ('BND', 'Brunei dollar'), ('BOB', 'Boliviano'), ('BOV', 'Bolivian Mvdol (funds code)'), ('BRL', 'Brazilian real'), ('BSD', 'Bahamian dollar'), ('BTN', 'Bhutanese ngultrum'), ('BWP', 'Botswana pula'), ('BYN', 'Belarusian ruble'), ('BZD', 'Belize dollar'), ('CAD', 'Canadian dollar'), ('CDF', 'Congolese franc'), ('CHF', 'Swiss franc'), ('CLP', 'Chilean peso'), ('CNY', 'Chinese yuan'), ('COP', 'Colombian peso'), ('CRC', 'Costa Rican colon'), ('CUC', 'Cuban convertible peso'), ('CUP', 'Cuban peso'), ('CVE', 'Cape Verdean escudo'), ('CZK', 'Czech koruna'), ('DJF', 'Djiboutian franc'), ('DKK', 'Danish krone'), ('DOP', 'Dominican peso'), ('DZD', 'Algerian dinar'), ('EGP', 'Egyptian pound'), ('ERN', 'Eritrean nakfa'), ('ETB', 'Ethiopian birr'), ('EUR', 'Euro'), ('FJD', 'Fiji dollar'), ('FKP', 'Falkland Islands pound'), ('GBP', 'Pound sterling'), ('GEL', 'Georgian lari'), ('GHS', 'Ghanaian cedi'), ('GIP', 'Gibraltar pound'), ('GMD', 'Gambian dalasi'), ('GNF', 'Guinean franc'), ('GTQ', 'Guatemalan quetzal'), ('GYD', 'Guyanese dollar'), ('HKD', 'Hong Kong dollar'), ('HNL', 'Honduran lempira'), ('HRK', 'Croatian kuna'), ('HTG', 'Haitian gourde'), ('HUF', 'Hungarian forint'), ('IDR', 'Indonesian rupiah'), ('ILS', 'Israeli new shekel'), ('INR', 'Indian rupee'), ('IQD', 'Iraqi dinar'), ('IRR', 'Iranian rial'), ('ISK', 'Icelandic króna'), ('JMD', 'Jamaican dollar'), ('JOD', 'Jordanian dinar'), ('JPY', 'Japanese yen'), ('KES', 'Kenyan shilling'), ('KGS', 'Kyrgyzstani som'), ('KHR', 'Cambodian riel'), ('KMF', 'Comoro franc'), ('KPW', 'North Korean won'), ('KRW', 'South Korean won'), ('KWD', 'Kuwaiti dinar'), ('KYD', 'Cayman Islands dollar'), ('KZT', 'Kazakhstani tenge'), ('LAK', 'Lao kip'), ('LBP', 'Lebanese pound'), ('LKR', 'Sri Lankan rupee'), ('LRD', 'Liberian dollar'), ('LSL', 'Lesotho loti'), ('LYD', 'Libyan dinar'), ('MAD', 'Moroccan dirham'), ('MDL', 'Moldovan leu'), ('MGA', 'Malagasy ariary'), ('MKD', 'Macedonian denar'), ('MMK', 'Myanmar kyat'), ('MNT', 'Mongolian tögrög'), ('MOP', 'Macanese pataca'), ('MRU', 'Mauritanian ouguiya'), ('MUR', 'Mauritian rupee'), ('MVR', 'Maldivian rufiyaa'), ('MWK', 'Malawian kwacha'), ('MXN', 'Mexican peso'), ('MYR', 'Malaysian ringgit'), ('MZN', 'Mozambican metical'), ('NAD', 'Namibian dollar'), ('NGN', 'Nigerian naira'), ('NIO', 'Nicaraguan córdoba'), ('NOK', 'Norwegian krone'), ('NPR', 'Nepalese rupee'), ('NZD', 'New Zealand dollar'), ('OMR', 'Omani rial'), ('PAB', 'Panamanian balboa'), ('PEN', 'Peruvian sol'), ('PGK', 'Papua New Guinean kina'), ('PHP', 'Philippine peso'), ('PKR', 'Pakistani rupee'), ('PLN', 'Polish złoty'), ('PYG', 'Paraguayan guaraní'), ('QAR', 'Qatari riyal'), ('RON', 'Romanian leu'), ('RSD', 'Serbian dinar'), ('RUB', 'Russian ruble'), ('RWF', 'Rwandan franc'), ('SAR', 'Saudi riyal'), ('SBD', 'Solomon Islands dollar'), ('SCR', 'Seychelles rupee'), ('SDG', 'Sudanese pound'), ('SEK', 'Swedish krona/kronor'), ('SGD', 'Singapore dollar'), ('SHP', 'Saint Helena pound'), ('SLL', 'Sierra Leonean leone'), ('SOS', 'Somali shilling'), ('SRD', 'Surinamese dollar'), ('SSP', 'South Sudanese pound'), ('STN', 'São Tomé and Príncipe dobra'), ('SVC', 'Salvadoran colón'), ('SYP', 'Syrian pound'), ('SZL', 'Swazi lilangeni'), ('THB', 'Thai baht'), ('TJS', 'Tajikistani somoni'), ('TMT', 'Turkmenistan manat'), ('TND', 'Tunisian dinar'), ('TOP', 'Tongan paʻanga'), ('TRY', 'Turkish lira'), ('TTD', 'Trinidad and Tobago dollar'), ('TWD', 'New Taiwan dollar'), ('TZS', 'Tanzanian shilling'), ('UAH', 'Ukrainian hryvnia'), ('UGX', 'Ugandan shilling'), ('USD', 'United States dollar'), ('UYU', 'Uruguayan peso'), ('UYW', 'Unidad previsional[14]'), ('UZS', 'Uzbekistan som'), ('VES', 'Venezuelan bolívar soberano'), ('VND', 'Vietnamese đồng'), ('VUV', 'Vanuatu vatu'), ('WST', 'Samoan tala'), ('XAF', 'CFA franc BEAC'), ('XAG', 'Silver (one troy ounce)'), ('XAU', 'Gold (one troy ounce)'), ('XCD', 'East Caribbean dollar'), ('XOF', 'CFA franc BCEAO'), ('XPF', 'CFP franc (franc Pacifique)'), ('YER', 'Yemeni rial'), ('ZAR', 'South African rand'), ('ZMW', 'Zambian kwacha'), ('ZWL', 'Zimbabwean dollar')], default='', max_length=250),
        ),
        migrations.AddField(
            model_name='household',
            name='female_age_group_18_59_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='female_age_group_18_59_disabled_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='female_age_group_60_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='female_age_group_60_disabled_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='male_age_group_18_59_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='male_age_group_18_59_disabled_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='male_age_group_60_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='male_age_group_60_disabled_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='registration_method',
            field=models.CharField(choices=[('', 'None'), ('HH_REGISTRATION', 'Household Registration'), ('COMMUNITY', 'Community-level Registration')], default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='country',
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name='household',
            name='country',
            field=django_countries.fields.CountryField(max_length=2),
        ),
        migrations.AlterField(
            model_name='household',
            name='female_age_group_0_5_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='female_age_group_0_5_disabled_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='female_age_group_12_17_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='female_age_group_12_17_disabled_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='female_age_group_6_11_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='female_age_group_6_11_disabled_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='first_registration_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='household',
            name='last_registration_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='household',
            name='male_age_group_0_5_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='male_age_group_0_5_disabled_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='male_age_group_12_17_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='male_age_group_12_17_disabled_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='male_age_group_6_11_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='male_age_group_6_11_disabled_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='pregnant_count',
            field=models.PositiveIntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='returnee',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='administration_of_rutf',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='enrolled_in_nutrition_programme',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='full_name',
            field=models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(2)]),
        ),
        migrations.AlterField(
            model_name='individual',
            name='marital_status',
            field=models.CharField(choices=[('', 'None'), ('SINGLE', 'Single'), ('MARRIED', 'Married'), ('WIDOWED', 'Widowed'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated')], default='', max_length=255),
        ),
        migrations.AddField(
            model_name='household',
            name='collect_individual_data',
            field=models.CharField(choices=[('', 'None'), ('1', 'Yes'), ('0', 'No')], default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='individual',
            name='work_status',
            field=models.CharField(blank=True, choices=[('1', 'Yes'), ('0', 'No'), ('NOT_PROVIDED', 'Not provided')], default='NOT_PROVIDED', max_length=20),
        ),
        migrations.AddField(
            model_name='household',
            name='unhcr_id',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='household',
            name='unicef_id',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='individual',
            name='enrolled_in_nutrition_programme',
            field=models.BooleanField(null=True),
        ),
        migrations.DeleteModel(
            name='HouseholdIdentity',
        ),
        migrations.AddField(
            model_name='household',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=0, help_text='record revision number'),
        ),
        migrations.AddField(
            model_name='individual',
            name='version',
            field=concurrency.fields.IntegerVersionField(default=0, help_text='record revision number'),
        ),
        migrations.AlterModelOptions(
            name='household',
            options={'verbose_name': 'Household'},
        ),
        migrations.AlterModelOptions(
            name='individual',
            options={'verbose_name': 'Individual'},
        ),
        migrations.RemoveField(
            model_name='household',
            name='status',
        ),
        migrations.RemoveField(
            model_name='individual',
            name='status',
        ),
        migrations.AddField(
            model_name='individual',
            name='duplicate',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='individual',
            name='withdrawn',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='household',
            name='withdrawn',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='household',
            name='removed_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='withdrawn_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='duplicate_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='removed_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='withdrawn_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='flex_fields',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='household',
            name='last_sync_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='flex_fields',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='individual',
            name='last_sync_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='individualroleinhousehold',
            name='last_sync_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
