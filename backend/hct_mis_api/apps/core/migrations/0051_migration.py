# Generated by Django 3.2.13 on 2022-06-24 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='countrycodemap',
            options={'ordering': ('country_new',)},
        ),
        migrations.RemoveField(
            model_name='countrycodemap',
            name='country',
        ),
    ]
