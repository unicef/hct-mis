# Generated by Django 3.2.23 on 2024-02-07 13:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0169_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='individual',
            name='kobo_asset_id',
        ),
        migrations.RemoveField(
            model_name='individual',
            name='row_id',
        ),
    ]
