# Generated by Django 3.2.13 on 2022-06-27 15:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0111_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='household',
            name='country',
        ),
        migrations.RemoveField(
            model_name='household',
            name='country_origin',
        ),
    ]
