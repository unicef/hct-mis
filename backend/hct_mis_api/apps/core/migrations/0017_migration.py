# Generated by Django 2.2.16 on 2021-02-10 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='countrycodemap',
            options={'ordering': ('country',)},
        ),
    ]
