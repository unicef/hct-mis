# Generated by Django 3.2.20 on 2023-09-19 12:50

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0108_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverymechanismperpaymentplan',
            name='bank_account_number',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='deliverymechanismperpaymentplan',
            name='bank_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='deliverymechanismperpaymentplan',
            name='card_number',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='deliverymechanismperpaymentplan',
            name='phone_no',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
    ]
