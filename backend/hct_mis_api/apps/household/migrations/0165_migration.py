# Generated by Django 3.2.23 on 2024-01-04 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0164_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='household',
            name='size',
            field=models.PositiveIntegerField(blank=True, db_index=True, null=True),
        ),
    ]
