# Generated by Django 2.2.8 on 2020-07-14 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0009_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashplan',
            name='verification_status',
            field=models.CharField(default='PENDING', max_length=200),
        ),
    ]
