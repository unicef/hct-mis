# Generated by Django 2.2.8 on 2020-07-16 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sanction_list', '0006_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sanctionlistindividual',
            name='second_name',
            field=models.CharField(blank=True, default='', max_length=85),
        ),
    ]
