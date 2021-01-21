# Generated by Django 2.2.16 on 2021-01-19 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0002_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='country',
        ),
        migrations.AddField(
            model_name='report',
            name='number_of_records',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='report_type',
            field=models.IntegerField(choices=[(1, 'Individuals'), (2, 'Households'), (3, 'Cash Plan Verification'), (4, 'Payments'), (5, 'Payment verification'), (6, 'Cash Plan'), (7, 'Programme'), (8, 'Individuals & Payment')]),
        ),
    ]
