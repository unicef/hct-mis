# Generated by Django 2.2.16 on 2021-02-16 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steficon', '0005_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='rule',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
