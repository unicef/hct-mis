# Generated by Django 3.2.24 on 2024-03-13 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0109_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='importedhousehold',
            name='social_worker',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='importedindividual',
            name='social_worker',
            field=models.BooleanField(default=False),
        ),
    ]
