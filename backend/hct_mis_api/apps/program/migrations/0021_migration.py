# Generated by Django 2.2.16 on 2021-02-12 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0002_migration_squashed_0020_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashplan',
            name='delivery_type',
            field=models.CharField(choices=[('CASH', 'Cash'), ('DEPOSIT_TO_CARD', 'Deposit to Card'), ('TRANSFER', 'Transfer')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='down_payment',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='funds_commitment',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='vision_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
