# Generated by Django 2.2.8 on 2020-07-07 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mis_datahub', '0008_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='program',
            name='status',
        ),
    ]
