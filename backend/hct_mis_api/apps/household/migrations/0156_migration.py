# Generated by Django 3.2.20 on 2023-09-05 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0155_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='entitlementcard',
            name='is_original',
            field=models.BooleanField(default=True),
        ),
    ]
