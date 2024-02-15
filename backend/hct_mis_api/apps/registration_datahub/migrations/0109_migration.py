# Generated by Django 3.2.23 on 2024-02-13 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0108_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='importedhousehold',
            name='detail_id',
            field=models.CharField(blank=True, help_text='Kobo asset ID, Xlsx row ID, Aurora source ID', max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='importedindividual',
            name='detail_id',
            field=models.CharField(blank=True, help_text='Kobo asset ID, Xlsx row ID, Aurora source ID', max_length=150, null=True),
        ),
    ]
