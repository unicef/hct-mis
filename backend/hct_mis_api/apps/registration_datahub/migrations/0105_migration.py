# Generated by Django 3.2.22 on 2023-12-19 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0104_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='importdata',
            name='program_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
