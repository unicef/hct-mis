# Generated by Django 2.2.16 on 2022-01-14 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('power_query', '0002_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='error',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]
