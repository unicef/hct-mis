# Generated by Django 2.2.16 on 2021-02-12 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flexibleattributegroup',
            name='removed_date',
        ),
    ]
