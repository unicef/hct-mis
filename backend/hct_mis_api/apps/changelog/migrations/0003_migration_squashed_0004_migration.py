# Generated by Django 3.2.24 on 2024-02-16 05:13

from django.db import migrations


class Migration(migrations.Migration):

    replaces = [('changelog', '0003_migration'), ('changelog', '0004_migration')]

    dependencies = [
        ('changelog', '0001_migration_squashed_0002_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='changelog',
            options={'ordering': ('-date',)},
        ),
    ]
