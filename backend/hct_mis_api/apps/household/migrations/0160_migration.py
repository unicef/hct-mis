# Generated by Django 3.2.22 on 2023-10-24 23:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0159_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='household',
            name='data_collecting_type',
        ),
    ]
