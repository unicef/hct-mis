# Generated by Django 3.2.23 on 2024-02-19 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0118_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentplansplit',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
