# Generated by Django 3.2.23 on 2024-01-08 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0105_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importedhousehold',
            name='size',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
