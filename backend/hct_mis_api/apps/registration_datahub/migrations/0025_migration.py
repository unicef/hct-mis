# Generated by Django 2.2.8 on 2020-10-16 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0024_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='importedhousehold',
            name='consent',
            field=models.BooleanField(default=True),
        ),
    ]
