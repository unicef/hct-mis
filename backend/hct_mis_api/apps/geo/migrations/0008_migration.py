# Generated by Django 3.2.22 on 2023-11-09 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0007_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='area',
            options={'ordering': ('name',), 'verbose_name_plural': 'Areas'},
        ),
    ]