# Generated by Django 3.2.20 on 2023-08-23 11:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('changelog', '0003_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='changelog',
            options={'ordering': ('-date',)},
        ),
    ]
