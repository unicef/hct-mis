# Generated by Django 3.2.15 on 2022-09-13 11:31

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0119_migration'),
        ('core', '0059_migration'),
        ('payment', '0068_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialserviceprovider',
            name='distribution_limit',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, help_text='The maximum amount of money that can be distributed or unlimited if null', max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='assigned_payment_channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='payment.paymentchannel'),
        ),
        migrations.AlterField(
            model_name='paymentchannel',
            name='individual',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_channels', to='household.individual'),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='export_per_fsp_zip_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.filetemp'),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='export_xlsx_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.filetemp'),
        ),
        migrations.AlterField(
            model_name='paymentplan',
            name='imported_xlsx_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.filetemp'),
        ),
    ]
