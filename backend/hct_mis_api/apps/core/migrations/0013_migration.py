# Generated by Django 2.2.16 on 2021-01-28 22:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adminarea',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='adminarea',
            name='longitude',
        ),
    ]
