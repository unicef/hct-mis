# Generated by Django 3.2.25 on 2024-03-16 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0077_migration'),
        ('steficon', '0018_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='allowed_business_areas',
            field=models.ManyToManyField(to='core.BusinessArea'),
        ),
    ]
