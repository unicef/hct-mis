# Generated by Django 3.2.25 on 2024-04-22 21:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration_data', '0035_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registrationdataimport',
            name='import_data',
        ),
        migrations.RemoveField(
            model_name='registrationdataimport',
            name='import_done',
        ),
    ]
