# Generated by Django 3.2.25 on 2024-09-10 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targeting', '0046_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetingcriteriarulefilter',
            name='round_number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
