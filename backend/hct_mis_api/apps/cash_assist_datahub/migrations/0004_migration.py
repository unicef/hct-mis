# Generated by Django 2.2.8 on 2020-06-26 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_assist_datahub', '0003_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashplan',
            name='status',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='entitlement_card_status',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='paymentrecord',
            name='status',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
