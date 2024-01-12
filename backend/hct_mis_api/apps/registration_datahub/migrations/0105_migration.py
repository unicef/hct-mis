# Generated by Django 3.2.23 on 2024-01-04 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0104_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='importedbankaccountinfo',
            name='account_holder_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='importedbankaccountinfo',
            name='bank_branch_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]