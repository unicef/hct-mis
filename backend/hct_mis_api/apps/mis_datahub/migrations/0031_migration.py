# Generated by Django 2.2.16 on 2021-06-08 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mis_datahub', '0030_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='DownPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rec_serial_number', models.CharField(blank=True, max_length=10, null=True)),
                ('business_area', models.CharField(max_length=4)),
                ('down_payment_reference', models.CharField(max_length=20)),
                ('document_type', models.CharField(max_length=10)),
                ('consumed_fc_number', models.CharField(max_length=10)),
                ('total_down_payment_amount_local', models.DecimalField(decimal_places=2, max_digits=15)),
                ('total_down_payment_amount_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('currency_code', models.CharField(blank=True, max_length=5, null=True)),
                ('posting_date', models.DateField(blank=True, null=True)),
                ('doc_year', models.IntegerField(blank=True, null=True)),
                ('doc_number', models.CharField(blank=True, max_length=10, null=True)),
                ('doc_item_number', models.CharField(max_length=3, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('updated_by', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('mis_sync_flag', models.BooleanField(blank=True, default=False, null=True)),
                ('mis_sync_date', models.DateTimeField(blank=True, null=True)),
                ('ca_sync_flag', models.BooleanField(blank=True, default=False, null=True)),
                ('ca_sync_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FundsCommitment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rec_serial_number', models.CharField(blank=True, max_length=10, null=True)),
                ('business_area', models.CharField(blank=True, max_length=4, null=True)),
                ('funds_commitment_number', models.CharField(blank=True, max_length=10, null=True)),
                ('document_type', models.CharField(blank=True, max_length=2, null=True)),
                ('document_text', models.CharField(blank=True, max_length=50, null=True)),
                ('currency_code', models.CharField(blank=True, max_length=5, null=True)),
                ('gl_account', models.CharField(blank=True, max_length=10, null=True)),
                ('commitment_amount_local', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('commitment_amount_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('total_open_amount_local', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('total_open_amount_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('vendor_id', models.CharField(blank=True, max_length=10, null=True)),
                ('posting_date', models.DateField(blank=True, null=True)),
                ('vision_approval', models.CharField(blank=True, max_length=1, null=True)),
                ('document_reference', models.CharField(max_length=16, null=True)),
                ('fc_status', models.CharField(blank=True, max_length=1, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('updated_by', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('mis_sync_flag', models.BooleanField(blank=True, default=False, null=True)),
                ('mis_sync_date', models.DateTimeField(blank=True, null=True)),
                ('ca_sync_flag', models.BooleanField(blank=True, default=False, null=True)),
                ('ca_sync_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
