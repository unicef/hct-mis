# Generated by Django 3.2.25 on 2024-03-24 20:31

from django.db import migrations, models
import hct_mis_api.apps.account.models


def add_payment_gateway_fsp_mobile_money_delivery_mechanism(apps, schema_editor):
    FinancialServiceProvider = apps.get_model("payment", "FinancialServiceProvider")

    for fsp in FinancialServiceProvider.objects.filter(payment_gateway_id__isnull=False):
        fsp.delivery_mechanisms = ["Cash over the counter", "Mobile Money"]
        fsp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0123_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverymechanismperpaymentplan',
            name='chosen_configuration',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='delivery_type',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'),
                                            ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'),
                                            ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'),
                                            ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'),
                                            ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'),
                                            ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter')],
                                   db_index=True, max_length=24, null=True),
        ),
        migrations.AlterField(
            model_name='deliverymechanismperpaymentplan',
            name='delivery_mechanism',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'),
                                            ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'),
                                            ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'),
                                            ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'),
                                            ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'),
                                            ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter')],
                                   db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='financialserviceprovider',
            name='delivery_mechanisms',
            field=hct_mis_api.apps.account.models.HorizontalChoiceArrayField(base_field=models.CharField(
                choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'),
                         ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'), ('Deposit to Card', 'Deposit to Card'),
                         ('Mobile Money', 'Mobile Money'), ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'),
                         ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'),
                         ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter')], max_length=24),
                                                                             size=None),
        ),
        migrations.AlterField(
            model_name='fspxlsxtemplateperdeliverymechanism',
            name='delivery_mechanism',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'),
                                            ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'),
                                            ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'),
                                            ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'),
                                            ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'),
                                            ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter')],
                                   max_length=255, verbose_name='Delivery Mechanism'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='delivery_type',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'),
                                            ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'),
                                            ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'),
                                            ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'),
                                            ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'),
                                            ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter')],
                                   max_length=24, null=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='delivery_type',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'),
                                            ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'),
                                            ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'),
                                            ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'),
                                            ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'),
                                            ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter')],
                                   max_length=24, null=True),
        ),
        migrations.RunPython(add_payment_gateway_fsp_mobile_money_delivery_mechanism, migrations.RunPython.noop),
    ]
