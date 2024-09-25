# Generated by Django 3.2.25 on 2024-09-23 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mis_datahub', '0053_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fundscommitment',
            name='rec_serial_number',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='fundscommitment',
            unique_together={('funds_commitment_number', 'funds_commitment_item')},
        ),
    ]
