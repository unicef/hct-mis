# Generated by Django 2.2.8 on 2020-10-26 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0026_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='registrationdataimportdatahub',
            options={'ordering': ('name',)},
        ),
    ]
