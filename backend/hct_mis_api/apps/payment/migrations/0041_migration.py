# Generated by Django 2.2.26 on 2022-02-17 15:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0040_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentrecord',
            name='is_included',
        ),
    ]
