# Generated by Django 2.2.8 on 2020-05-11 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_migration'),
        ('program', '0002_migration'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='program',
            unique_together={('name', 'business_area')},
        ),
    ]
