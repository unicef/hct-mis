# Generated by Django 2.2.16 on 2021-07-01 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cash_assist_datahub', '0011_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='sentry_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='traceback',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
