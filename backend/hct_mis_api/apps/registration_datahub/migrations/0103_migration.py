# Generated by Django 3.2.20 on 2023-09-26 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0102_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='importedhousehold',
            name='data_collecting_type_id',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
