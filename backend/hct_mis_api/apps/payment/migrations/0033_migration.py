# Generated by Django 2.2.26 on 2022-02-15 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0032_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrecord',
            name='is_included',
            field=models.BooleanField(default=False),
        ),
    ]
