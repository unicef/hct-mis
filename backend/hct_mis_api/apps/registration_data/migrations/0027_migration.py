# Generated by Django 3.2.19 on 2023-07-16 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_data', '0026_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationdataimport',
            name='erased',
            field=models.BooleanField(default=False, help_text='Abort RDI'),
        ),
    ]
