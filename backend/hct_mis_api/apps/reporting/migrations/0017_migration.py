# Generated by Django 3.2.23 on 2024-01-04 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0016_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardreport',
            name='year',
            field=models.PositiveSmallIntegerField(default=2024),
        ),
    ]
