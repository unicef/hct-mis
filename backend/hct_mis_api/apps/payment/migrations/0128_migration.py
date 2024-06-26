# Generated by Django 3.2.25 on 2024-05-08 11:01

from django.db import migrations, models
import hct_mis_api.apps.account.models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0127_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='transaction_status_blockchain_link',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='transaction_status_blockchain_link',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='delivery_type',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'), ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'), ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'), ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'), ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'), ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter'), ('Transfer to Digital Wallet', 'Transfer to Digital Wallet'), ('ATM Card', 'ATM Card')], db_index=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='deliverymechanismperpaymentplan',
            name='delivery_mechanism',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'), ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'), ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'), ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'), ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'), ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter'), ('Transfer to Digital Wallet', 'Transfer to Digital Wallet'), ('ATM Card', 'ATM Card')], db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='financialserviceprovider',
            name='delivery_mechanisms',
            field=hct_mis_api.apps.account.models.HorizontalChoiceArrayField(base_field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'), ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'), ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'), ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'), ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'), ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter'), ('Transfer to Digital Wallet', 'Transfer to Digital Wallet'), ('ATM Card', 'ATM Card')], max_length=32), size=None),
        ),
        migrations.AlterField(
            model_name='financialserviceproviderxlsxtemplate',
            name='columns',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('payment_id', 'Payment ID'), ('household_id', 'Household ID'), ('household_size', 'Household Size'), ('collector_name', 'Collector Name'), ('alternate_collector_full_name', 'Alternate collector Full Name'), ('alternate_collector_given_name', 'Alternate collector Given Name'), ('alternate_collector_middle_name', 'Alternate collector Middle Name'), ('alternate_collector_phone_no', 'Alternate collector phone number'), ('alternate_collector_document_numbers', 'Alternate collector Document numbers'), ('alternate_collector_sex', 'Alternate collector Gender'), ('payment_channel', 'Payment Channel'), ('fsp_name', 'FSP Name'), ('currency', 'Currency'), ('entitlement_quantity', 'Entitlement Quantity'), ('entitlement_quantity_usd', 'Entitlement Quantity USD'), ('delivered_quantity', 'Delivered Quantity'), ('delivery_date', 'Delivery Date'), ('reference_id', 'Reference id'), ('reason_for_unsuccessful_payment', 'Reason for unsuccessful payment'), ('order_number', 'Order Number'), ('token_number', 'Token Number'), ('additional_collector_name', 'Additional Collector Name'), ('additional_document_type', 'Additional Document Type'), ('additional_document_number', 'Additional Document Number'), ('registration_token', 'Registration Token'), ('status', 'Status'), ('transaction_status_blockchain_link', 'Transaction Status on the Blockchain')], default=['payment_id', 'household_id', 'household_size', 'collector_name', 'alternate_collector_full_name', 'alternate_collector_given_name', 'alternate_collector_middle_name', 'alternate_collector_phone_no', 'alternate_collector_document_numbers', 'alternate_collector_sex', 'payment_channel', 'fsp_name', 'currency', 'entitlement_quantity', 'entitlement_quantity_usd', 'delivered_quantity', 'delivery_date', 'reference_id', 'reason_for_unsuccessful_payment', 'order_number', 'token_number', 'additional_collector_name', 'additional_document_type', 'additional_document_number', 'registration_token', 'status', 'transaction_status_blockchain_link'], help_text='Select the columns to include in the report', max_length=1000, verbose_name='Columns'),
        ),
        migrations.AlterField(
            model_name='fspxlsxtemplateperdeliverymechanism',
            name='delivery_mechanism',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'), ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'), ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'), ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'), ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'), ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter'), ('Transfer to Digital Wallet', 'Transfer to Digital Wallet'), ('ATM Card', 'ATM Card')], max_length=255, verbose_name='Delivery Mechanism'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='delivery_type',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'), ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'), ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'), ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'), ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'), ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter'), ('Transfer to Digital Wallet', 'Transfer to Digital Wallet'), ('ATM Card', 'ATM Card')], max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='currency',
            field=models.CharField(choices=[('', 'None'), ('AED', 'United Arab Emirates dirham'), ('AFN', 'Afghan afghani'), ('ALL', 'Albanian lek'), ('AMD', 'Armenian dram'), ('ANG', 'Netherlands Antillean guilder'), ('AOA', 'Angolan kwanza'), ('ARS', 'Argentine peso'), ('AUD', 'Australian dollar'), ('AWG', 'Aruban florin'), ('AZN', 'Azerbaijani manat'), ('BAM', 'Bosnia and Herzegovina convertible mark'), ('BBD', 'Barbados dollar'), ('BDT', 'Bangladeshi taka'), ('BGN', 'Bulgarian lev'), ('BHD', 'Bahraini dinar'), ('BIF', 'Burundian franc'), ('BMD', 'Bermudian dollar'), ('BND', 'Brunei dollar'), ('BOB', 'Boliviano'), ('BOV', 'Bolivian Mvdol (funds code)'), ('BRL', 'Brazilian real'), ('BSD', 'Bahamian dollar'), ('BTN', 'Bhutanese ngultrum'), ('BWP', 'Botswana pula'), ('BYN', 'Belarusian ruble'), ('BZD', 'Belize dollar'), ('CAD', 'Canadian dollar'), ('CDF', 'Congolese franc'), ('CHF', 'Swiss franc'), ('CLP', 'Chilean peso'), ('CNY', 'Chinese yuan'), ('COP', 'Colombian peso'), ('CRC', 'Costa Rican colon'), ('CUC', 'Cuban convertible peso'), ('CUP', 'Cuban peso'), ('CVE', 'Cape Verdean escudo'), ('CZK', 'Czech koruna'), ('DJF', 'Djiboutian franc'), ('DKK', 'Danish krone'), ('DOP', 'Dominican peso'), ('DZD', 'Algerian dinar'), ('EGP', 'Egyptian pound'), ('ERN', 'Eritrean nakfa'), ('ETB', 'Ethiopian birr'), ('EUR', 'Euro'), ('FJD', 'Fiji dollar'), ('FKP', 'Falkland Islands pound'), ('GBP', 'Pound sterling'), ('GEL', 'Georgian lari'), ('GHS', 'Ghanaian cedi'), ('GIP', 'Gibraltar pound'), ('GMD', 'Gambian dalasi'), ('GNF', 'Guinean franc'), ('GTQ', 'Guatemalan quetzal'), ('GYD', 'Guyanese dollar'), ('HKD', 'Hong Kong dollar'), ('HNL', 'Honduran lempira'), ('HRK', 'Croatian kuna'), ('HTG', 'Haitian gourde'), ('HUF', 'Hungarian forint'), ('IDR', 'Indonesian rupiah'), ('ILS', 'Israeli new shekel'), ('INR', 'Indian rupee'), ('IQD', 'Iraqi dinar'), ('IRR', 'Iranian rial'), ('ISK', 'Icelandic króna'), ('JMD', 'Jamaican dollar'), ('JOD', 'Jordanian dinar'), ('JPY', 'Japanese yen'), ('KES', 'Kenyan shilling'), ('KGS', 'Kyrgyzstani som'), ('KHR', 'Cambodian riel'), ('KMF', 'Comoro franc'), ('KPW', 'North Korean won'), ('KRW', 'South Korean won'), ('KWD', 'Kuwaiti dinar'), ('KYD', 'Cayman Islands dollar'), ('KZT', 'Kazakhstani tenge'), ('LAK', 'Lao kip'), ('LBP', 'Lebanese pound'), ('LKR', 'Sri Lankan rupee'), ('LRD', 'Liberian dollar'), ('LSL', 'Lesotho loti'), ('LYD', 'Libyan dinar'), ('MAD', 'Moroccan dirham'), ('MDL', 'Moldovan leu'), ('MGA', 'Malagasy ariary'), ('MKD', 'Macedonian denar'), ('MMK', 'Myanmar kyat'), ('MNT', 'Mongolian tögrög'), ('MOP', 'Macanese pataca'), ('MRU', 'Mauritanian ouguiya'), ('MUR', 'Mauritian rupee'), ('MVR', 'Maldivian rufiyaa'), ('MWK', 'Malawian kwacha'), ('MXN', 'Mexican peso'), ('MYR', 'Malaysian ringgit'), ('MZN', 'Mozambican metical'), ('NAD', 'Namibian dollar'), ('NGN', 'Nigerian naira'), ('NIO', 'Nicaraguan córdoba'), ('NOK', 'Norwegian krone'), ('NPR', 'Nepalese rupee'), ('NZD', 'New Zealand dollar'), ('OMR', 'Omani rial'), ('PAB', 'Panamanian balboa'), ('PEN', 'Peruvian sol'), ('PGK', 'Papua New Guinean kina'), ('PHP', 'Philippine peso'), ('PKR', 'Pakistani rupee'), ('PLN', 'Polish złoty'), ('PYG', 'Paraguayan guaraní'), ('QAR', 'Qatari riyal'), ('RON', 'Romanian leu'), ('RSD', 'Serbian dinar'), ('RUB', 'Russian ruble'), ('RWF', 'Rwandan franc'), ('SAR', 'Saudi riyal'), ('SBD', 'Solomon Islands dollar'), ('SCR', 'Seychelles rupee'), ('SDG', 'Sudanese pound'), ('SEK', 'Swedish krona/kronor'), ('SGD', 'Singapore dollar'), ('SHP', 'Saint Helena pound'), ('SLL', 'Sierra Leonean leone'), ('SOS', 'Somali shilling'), ('SRD', 'Surinamese dollar'), ('SSP', 'South Sudanese pound'), ('STN', 'São Tomé and Príncipe dobra'), ('SVC', 'Salvadoran colón'), ('SYP', 'Syrian pound'), ('SZL', 'Swazi lilangeni'), ('THB', 'Thai baht'), ('TJS', 'Tajikistani somoni'), ('TMT', 'Turkmenistan manat'), ('TND', 'Tunisian dinar'), ('TOP', 'Tongan paʻanga'), ('TRY', 'Turkish lira'), ('TTD', 'Trinidad and Tobago dollar'), ('TWD', 'New Taiwan dollar'), ('TZS', 'Tanzanian shilling'), ('UAH', 'Ukrainian hryvnia'), ('UGX', 'Ugandan shilling'), ('USD', 'United States dollar'), ('UYU', 'Uruguayan peso'), ('UYW', 'Unidad previsional[14]'), ('UZS', 'Uzbekistan som'), ('VES', 'Venezuelan bolívar soberano'), ('VND', 'Vietnamese đồng'), ('VUV', 'Vanuatu vatu'), ('WST', 'Samoan tala'), ('XAF', 'CFA franc BEAC'), ('XAG', 'Silver (one troy ounce)'), ('XAU', 'Gold (one troy ounce)'), ('XCD', 'East Caribbean dollar'), ('XOF', 'CFA franc BCEAO'), ('XPF', 'CFP franc (franc Pacifique)'), ('YER', 'Yemeni rial'), ('ZAR', 'South African rand'), ('ZMW', 'Zambian kwacha'), ('ZWL', 'Zimbabwean dollar'), ('USDC', 'USD Coin')], max_length=4),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='delivery_type',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'), ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'), ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'), ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'), ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'), ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter'), ('Transfer to Digital Wallet', 'Transfer to Digital Wallet'), ('ATM Card', 'ATM Card')], max_length=32, null=True),
        ),
    ]
