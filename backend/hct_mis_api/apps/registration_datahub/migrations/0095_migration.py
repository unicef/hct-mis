# Generated by Django 3.2.18 on 2023-04-06 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0094_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='importedindividual',
            name='email',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
