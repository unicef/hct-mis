# Generated by Django 3.2.22 on 2023-10-29 20:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0111_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='copied_from',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='is_migration_handled',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='is_original',
        ),
        migrations.RemoveField(
            model_name='paymentrecord',
            name='copied_from',
        ),
        migrations.RemoveField(
            model_name='paymentrecord',
            name='is_migration_handled',
        ),
        migrations.RemoveField(
            model_name='paymentrecord',
            name='is_original',
        ),
    ]
