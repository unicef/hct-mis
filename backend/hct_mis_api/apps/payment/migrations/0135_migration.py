# Generated by Django 3.2.25 on 2024-06-21 11:03

from django.db import migrations, models
import hct_mis_api.apps.account.models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0134_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialserviceproviderxlsxtemplate',
            name='columns',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('payment_id', 'Payment ID'), ('household_id', 'Household ID'), ('individual_id', 'Individual ID'), ('household_size', 'Household Size'), ('collector_name', 'Collector Name'), ('alternate_collector_full_name', 'Alternate collector Full Name'), ('alternate_collector_given_name', 'Alternate collector Given Name'), ('alternate_collector_middle_name', 'Alternate collector Middle Name'), ('alternate_collector_phone_no', 'Alternate collector phone number'), ('alternate_collector_document_numbers', 'Alternate collector Document numbers'), ('alternate_collector_sex', 'Alternate collector Gender'), ('payment_channel', 'Payment Channel'), ('fsp_name', 'FSP Name'), ('currency', 'Currency'), ('entitlement_quantity', 'Entitlement Quantity'), ('entitlement_quantity_usd', 'Entitlement Quantity USD'), ('delivered_quantity', 'Delivered Quantity'), ('delivery_date', 'Delivery Date'), ('reference_id', 'Reference id'), ('reason_for_unsuccessful_payment', 'Reason for unsuccessful payment'), ('order_number', 'Order Number'), ('token_number', 'Token Number'), ('additional_collector_name', 'Additional Collector Name'), ('additional_document_type', 'Additional Document Type'), ('additional_document_number', 'Additional Document Number'), ('registration_token', 'Registration Token'), ('status', 'Status'), ('transaction_status_blockchain_link', 'Transaction Status on the Blockchain')], default=['payment_id', 'household_id', 'individual_id', 'household_size', 'collector_name', 'alternate_collector_full_name', 'alternate_collector_given_name', 'alternate_collector_middle_name', 'alternate_collector_phone_no', 'alternate_collector_document_numbers', 'alternate_collector_sex', 'payment_channel', 'fsp_name', 'currency', 'entitlement_quantity', 'entitlement_quantity_usd', 'delivered_quantity', 'delivery_date', 'reference_id', 'reason_for_unsuccessful_payment', 'order_number', 'token_number', 'additional_collector_name', 'additional_document_type', 'additional_document_number', 'registration_token', 'status', 'transaction_status_blockchain_link'], help_text='Select the columns to include in the report', max_length=1000, verbose_name='Columns'),
        ),
        migrations.AlterField(
            model_name='financialserviceproviderxlsxtemplate',
            name='core_fields',
            field=hct_mis_api.apps.account.models.HorizontalChoiceArrayField(base_field=models.CharField(blank=True, choices=[('age', 'Age (calculated)'), ('residence_status', 'Residence status'), ('consent', 'Do you consent?'), ('consent_sign', 'Do you consent?'), ('country_origin', 'Country of Origin'), ('country', 'Country of registration'), ('address', 'Address'), ('zip_code', 'Zip code'), ('admin1', 'Household resides in which admin1?'), ('admin2', 'Household resides in which admin2?'), ('admin3', 'Household resides in which admin3?'), ('admin4', 'Household resides in which admin4?'), ('geopoint', 'Geolocation'), ('unhcr_id', 'UNHCR Case ID'), ('returnee', 'Is this a returnee Household?'), ('size', 'What is the Household size?'), ('fchild_hoh', 'Child is female and Head of Household'), ('child_hoh', 'Child is Head of Household'), ('relationship', 'Relationship to Head of Household'), ('full_name', 'Full name'), ('given_name', 'Given name'), ('middle_name', 'Middle name(s)'), ('family_name', 'Family name'), ('sex', 'Gender'), ('birth_date', 'Birth date'), ('estimated_birth_date', 'Estimated birth date?'), ('photo', "Individual's photo"), ('marital_status', 'Marital status'), ('phone_no', 'Phone number'), ('who_answers_phone', 'Who answers this phone?'), ('phone_no_alternative', 'Alternative phone number'), ('who_answers_alt_phone', 'Who answers this (alt) phone?'), ('registration_method', 'Method of collection (e.g. HH survey, Community, etc.)'), ('collect_individual_data', 'Will you be collecting all member Individual data?'), ('currency', 'Which currency will be used for financial questions?'), ('birth_certificate_no', 'Birth certificate number'), ('birth_certificate_issuer', 'Issuing country of birth certificate'), ('birth_certificate_photo', 'Birth certificate photo'), ('tax_id_no', 'Tax identification number'), ('tax_id_issuer', 'Issuing country of tax identification'), ('tax_id_photo', 'Tax identification photo'), ('drivers_license_no', "Driver's license number"), ('drivers_license_issuer', "Issuing country of driver's license"), ('drivers_license_photo', "Driver's license photo"), ('electoral_card_no', 'Electoral card number'), ('electoral_card_issuer', 'Issuing country of electoral card'), ('electoral_card_photo', 'Electoral card photo'), ('unhcr_id_no', 'UNHCR ID number'), ('unhcr_id_issuer', 'Issuing entity of UNHCR ID'), ('unhcr_id_photo', 'UNHCR ID photo'), ('national_passport', 'National passport number'), ('national_passport_issuer', 'Issuing country of national passport'), ('national_passport_photo', 'National passport photo'), ('national_id_no', 'National ID number'), ('national_id_issuer', 'Issuing country of national ID'), ('national_id_photo', 'National ID photo'), ('scope_id_no', 'WFP Scope ID number'), ('scope_id_issuer', 'Issuing entity of SCOPE ID'), ('scope_id_photo', 'WFP Scope ID photo'), ('other_id_type', 'If other type of ID, specify the type'), ('other_id_no', 'Other ID number'), ('other_id_issuer', 'Issuing country of other ID'), ('other_id_photo', 'ID photo'), ('female_age_group_0_5_count', 'Females Age 0 - 5'), ('female_age_group_6_11_count', 'Females Age 6 - 11'), ('female_age_group_12_17_count', 'Females Age 12 - 17'), ('female_age_group_18_59_count', 'Females Age 18 - 59'), ('female_age_group_60_count', 'Females Age 60 +'), ('pregnant_count', 'Pregnant count'), ('male_age_group_0_5_count', 'Males Age 0 - 5'), ('male_age_group_6_11_count', 'Males Age 6 - 11'), ('male_age_group_12_17_count', 'Males Age 12 - 17'), ('male_age_group_18_59_count', 'Males Age 18 - 59'), ('male_age_group_60_count', 'Males Age 60 +'), ('female_age_group_0_5_disabled_count', 'Females age 0 - 5 with disability'), ('female_age_group_6_11_disabled_count', 'Females age 6 - 11 with disability'), ('female_age_group_12_17_disabled_count', 'Females age 12 - 17 with disability'), ('female_age_group_18_59_disabled_count', 'Females Age 18 - 59 with disability'), ('female_age_group_60_disabled_count', 'Female members with Disability age 60 +'), ('male_age_group_0_5_disabled_count', 'Males age 0 - 5 with disability'), ('male_age_group_6_11_disabled_count', 'Males age 6 - 11 with disability'), ('male_age_group_12_17_disabled_count', 'Males age 12 - 17 with disability'), ('male_age_group_18_59_disabled_count', 'Males Age 18 - 59 with disability'), ('male_age_group_60_disabled_count', 'Male members with Disability age 60 +'), ('pregnant', 'Is the Individual pregnant?'), ('work_status', 'Does the Individual have paid employment in the current month?'), ('observed_disability', 'Does the Individual have disability?'), ('seeing_disability', 'If the Individual has difficulty seeing, what is the severity?'), ('hearing_disability', 'If the Individual has difficulty hearing, what is the severity?'), ('physical_disability', 'If the Individual has difficulty walking or climbing steps, what is the severity?'), ('memory_disability', 'If the Individual has difficulty remembering or concentrating, what is the severity?'), ('selfcare_disability', 'Do you have difficulty (with self-care such as) washing all over or dressing'), ('comms_disability', 'If the Individual has difficulty communicating, what is the severity?'), ('fchild_hoh', 'Female child headed Household'), ('child_hoh', 'Child headed Household'), ('village', 'Village'), ('deviceid', 'Device ID'), ('name_enumerator', 'Name of the enumerator'), ('org_enumerator', 'Organization of the enumerator'), ('consent_sharing', 'Which organizations may we share your information with?'), ('org_name_enumerator', 'Name of partner organization'), ('disability', 'Individual is disabled?'), ('first_registration_date', 'First Individual registration date'), ('first_registration_date', 'First Household registration date'), ('number_of_children', 'What is the number of children in the Household?'), ('has_phone_number', 'Has phone number?'), ('has_tax_id_number', 'Has tax ID number?'), ('has_the_bank_account_number', 'Has the bank account number?'), ('role', 'Role'), ('registration_data_import', 'Registration Data Import'), ('registration_data_import', 'Registration Data Import'), ('household_unicef_id', 'Household unicef id'), ('individual_unicef_id', 'Individual unicef id'), ('admin_area_title', 'Household resides in which admin area?'), ('start', 'Data collection start date'), ('end', 'Data collection end date'), ('primary_collector_id', 'List of primary collectors ids, separated by a semicolon'), ('alternate_collector_id', 'List of alternate collectors ids, separated by a semicolon'), ('household_id', 'Household ID'), ('household_id', 'Household ID'), ('email', 'Individual email'), ('preferred_language', 'Preferred language'), ('age_at_registration', 'Age at registration'), ('account_holder_name', 'Account holder name'), ('bank_branch_name', 'Bank branch name'), ('index_id', 'Index ID'), ('wallet_name', 'Wallet Name'), ('blockchain_name', 'Blockchain Name'), ('wallet_address', 'Wallet Address'), ('program_registration_id', 'Program registration id'), ('account_holder_name', 'Account holder name'), ('bank_branch_name', 'Bank branch name'), ('bank_name', 'Bank name'), ('bank_account_number', 'Bank account number'), ('debit_card_issuer', 'Debit Card Issuer'), ('debit_card_number', 'Debit card number'), ('payment_delivery_phone_no', 'Payment delivery phone number'), ('card_number_atm_card', 'Card number (ATM card)'), ('card_expiry_date_atm_card', 'Card expiry date (ATM card)'), ('name_of_cardholder_atm_card', 'Name of cardholder (ATM card)'), ('card_number_deposit_to_card', 'Card Number (Deposit to Card)'), ('delivery_phone_number_mobile_money', 'Delivery Phone Number (Mobile Money)'), ('provider_mobile_money', 'Provider (Mobile Money)'), ('bank_name_transfer_to_account', 'Bank Name (Transfer to Account)'), ('bank_account_number_transfer_to_account', 'Bank Account Number (Transfer to Account)'), ('mobile_phone_number_cash_over_the_counter', 'Mobile Phone Number (Cash Over the Counter)'), ('wallet_name_transfer_to_digital_wallet', 'Wallet Name'), ('blockchain_name_transfer_to_digital_wallet', 'Blockchain Name'), ('wallet_address_transfer_to_digital_wallet', 'Wallet Address')], max_length=255), blank=True, default=list, size=None),
        ),
    ]
