# Generated by Django 2.2.16 on 2021-02-18 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0005_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardreport',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='dashboardreport',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
