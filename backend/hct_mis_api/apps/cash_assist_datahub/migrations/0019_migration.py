# Generated by Django 3.2.25 on 2024-04-22 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_assist_datahub', '0018_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentrecord',
            name='delivery_type',
            field=models.CharField(choices=[('Cardless cash withdrawal', 'Cardless cash withdrawal'), ('Cash', 'Cash'), ('Cash by FSP', 'Cash by FSP'), ('Cheque', 'Cheque'), ('Deposit to Card', 'Deposit to Card'), ('Mobile Money', 'Mobile Money'), ('Pre-paid card', 'Pre-paid card'), ('Referral', 'Referral'), ('Transfer', 'Transfer'), ('Transfer to Account', 'Transfer to Account'), ('Voucher', 'Voucher'), ('Cash over the counter', 'Cash over the counter'), ('Transfer to Digital Wallet', 'Transfer to Digital Wallet')], default='Cash', max_length=32, null=True),
        ),
    ]
