# Generated by Django 2.2.16 on 2021-01-18 10:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0015_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cashplan',
            options={'verbose_name': 'Cash Plan'},
        ),
        migrations.AlterModelOptions(
            name='program',
            options={'verbose_name': 'Programme'},
        ),
    ]
