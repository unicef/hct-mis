# Generated by Django 3.2.15 on 2023-01-24 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('power_query', '0006_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='query',
            name='refresh_daily',
        ),
        migrations.RemoveField(
            model_name='report',
            name='refresh_daily',
        ),
        migrations.AddField(
            model_name='report',
            name='frequence',
            field=models.CharField(blank=True, help_text='Refresh every (e.g. 3 - 1/3 - mon - 1/3,Mon)',
                                   max_length=3, null=True),
        ),
    ]
