# Generated by Django 3.2.13 on 2022-06-24 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessarea',
            name='countries',
        ),
    ]