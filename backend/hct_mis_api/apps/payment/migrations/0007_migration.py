# Generated by Django 2.2.8 on 2020-06-22 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentrecord',
            name='cash_plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_records', to='program.CashPlan'),
        ),
    ]
