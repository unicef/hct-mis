# Generated by Django 3.2.20 on 2023-09-19 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0156_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='is_recalculated_group_ages',
            field=models.BooleanField(default=False),
        ),
    ]
