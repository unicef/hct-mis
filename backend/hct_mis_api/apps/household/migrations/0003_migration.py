# Generated by Django 2.2.8 on 2020-02-03 10:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0002_migration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='household',
            old_name='locations',
            new_name='location',
        ),
    ]
