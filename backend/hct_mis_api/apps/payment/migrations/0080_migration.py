# Generated by Django 3.2.15 on 2022-12-07 22:39

from django.db import migrations, models
import hct_mis_api.apps.payment.models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0079_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverymechanism',
            name='global_core_fields',
            field=hct_mis_api.apps.payment.models.ChoiceArrayField(base_field=models.CharField(blank=True, choices=[('age', 'Age (calculated)'), ('residence_status', 'Residence status'), ('consent', 'Do you consent?'), ('consent_sign', 'Do you consent?'), ('country_origin', 'Country of Origin'), ('country', 'Country of registration'), ('address', 'Address'), ('admin1', 'Household resides in which ${admin1_h_c}?'), ('admin2', 'Household resides in which ${admin2_h_c}?'), ('geopoint', 'Geolocation'), ('unhcr_id', 'UNHCR Case ID'), ('returnee', 'Is this a returnee household?'), ('size', 'What is the household size?'), ('fchild_hoh', 'Child is female and head of household'), ('child_hoh', 'Child is head of household'), ('relationship', 'Relationship to head of household'), ('full_name', 'Full name'), ('given_name', 'Given name'), ('middle_name', 'Middle name(s)'), ('family_name', 'Family name'), ('sex', 'Gender'), ('birth_date', 'Birth date'), ('estimated_birth_date', 'Estimated birth date?'), ('photo', "Individual's photo"), ('marital_status', 'Marital status'), ('phone_no', 'Phone number'), ('who_answers_phone', 'Who answers this phone?'), ('phone_no_alternative', 'Alternative phone number'), ('who_answers_alt_phone', 'Who answers this (alt) phone?'), ('registration_method', 'Method of collection (e.g. HH survey, Community, etc.)'), ('collect_individual_data', "Will you be collecting all member Individuals' data?"), ('currency', 'Which currency will be used for financial questions?'), ('birth_certificate_no', 'Birth certificate number'), ('birth_certificate_issuer', 'Issuing country of birth certificate'), ('birth_certificate_photo', 'Birth certificate photo'), ('drivers_license_no', "Driver's license number"), ('drivers_license_issuer', "Issuing country of driver's license"), ('drivers_license_photo', "Driver's license photo"), ('electoral_card_no', 'Electoral card number'), ('electoral_card_issuer', 'Issuing country of electoral card'), ('electoral_card_photo', 'Electoral card photo'), ('unhcr_id_no', 'UNHCR ID number'), ('unhcr_id_issuer', 'Issuing entity of UNHCR ID'), ('unhcr_id_photo', 'UNHCR ID photo'), ('national_passport', 'National passport number'), ('national_passport_issuer', 'Issuing country of national passport'), ('national_passport_photo', 'National passport photo'), ('national_id_no', 'National ID number'), ('national_id_issuer', 'Issuing country of national ID'), ('national_id_photo', 'National ID photo'), ('scope_id_no', 'WFP Scope ID number'), ('scope_id_issuer', 'Issuing entity of SCOPE ID'), ('scope_id_photo', 'WFP Scope ID photo'), ('other_id_type', 'If other type of ID, specify the type'), ('other_id_no', 'Other ID number'), ('other_id_issuer', 'Issuing country of other ID'), ('other_id_photo', 'ID photo'), ('female_age_group_0_5_count', 'Females Age 0 - 5'), ('female_age_group_6_11_count', 'Females Age 6 - 11'), ('female_age_group_12_17_count', 'Females Age 12 - 17'), ('female_age_group_18_59_count', 'Females Age 18 - 59'), ('female_age_group_60_count', 'Females Age 60 +'), ('pregnant_count', 'Pregnant count'), ('male_age_group_0_5_count', 'Males Age 0 - 5'), ('male_age_group_6_11_count', 'Males Age 6 - 11'), ('male_age_group_12_17_count', 'Males Age 12 - 17'), ('male_age_group_18_59_count', 'Males Age 18 - 59'), ('male_age_group_60_count', 'Males Age 60 +'), ('female_age_group_0_5_disabled_count', 'Females age 0 - 5 with disability'), ('female_age_group_6_11_disabled_count', 'Females age 6 - 11 with disability'), ('female_age_group_12_17_disabled_count', 'Females age 12 - 17 with disability'), ('female_age_group_18_59_disabled_count', 'Females Age 18 - 59 with disability'), ('female_age_group_60_disabled_count', 'Female members with Disability age 60 +'), ('male_age_group_0_5_disabled_count', 'Males age 0 - 5 with disability'), ('male_age_group_6_11_disabled_count', 'Males age 6 - 11 with disability'), ('male_age_group_12_17_disabled_count', 'Males age 12 - 17 with disability'), ('male_age_group_18_59_disabled_count', 'Males Age 18 - 59 with disability'), ('male_age_group_60_disabled_count', 'Male members with Disability age 60 +'), ('pregnant', 'Is the individual pregnant?'), ('work_status', 'Does the individual have paid employment in the current month?'), ('observed_disability', 'Does the individual have disability?'), ('seeing_disability', 'If the individual has difficulty seeing, what is the severity?'), ('hearing_disability', 'If the individual has difficulty hearing, what is the severity?'), ('physical_disability', 'If the individual has difficulty walking or climbing steps, what is the severity?'), ('memory_disability', 'If the individual has difficulty remembering or concentrating, what is the severity?'), ('selfcare_disability', 'Do you have difficulty (with self-care such as) washing all over or dressing'), ('comms_disability', 'If the individual has difficulty communicating, what is the severity?'), ('fchild_hoh', 'Female child headed household'), ('child_hoh', 'Child headed household'), ('village', 'Village'), ('deviceid', 'Device ID'), ('name_enumerator', 'Name of the enumerator'), ('org_enumerator', 'Organization of the enumerator'), ('consent_sharing', 'Which organizations may we share your information with?'), ('org_name_enumerator', 'Name of partner organization'), ('disability', 'Individual is disabled?')], max_length=255), default=list, size=None),
        ),
        migrations.AlterField(
            model_name='deliverymechanism',
            name='payment_channel_fields',
            field=hct_mis_api.apps.payment.models.ChoiceArrayField(base_field=models.CharField(blank=True, choices=[('bank_name', 'Bank name'), ('bank_account_number', 'Bank account number'), ('debit_card_issuer', 'Debit Card Issuer'), ('debit_card_number', 'Debit card number')], max_length=255), default=list, size=None),
        ),
    ]
