# Generated by Django 2.2.8 on 2020-04-23 16:39

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0022_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2),
        ),
    ]
