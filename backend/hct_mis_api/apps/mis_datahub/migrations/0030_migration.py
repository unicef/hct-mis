# Generated by Django 2.2.16 on 2021-02-25 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mis_datahub', '0029_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='individual',
            name='sanction_list_confirmed_match',
            field=models.BooleanField(default=False),
        ),
    ]
