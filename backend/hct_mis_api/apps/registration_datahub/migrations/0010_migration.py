# Generated by Django 2.2.8 on 2020-06-16 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0009_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationdataimportdatahub',
            name='business_area_slug',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]
