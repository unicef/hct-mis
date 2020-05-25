# Generated by Django 2.2.8 on 2020-05-19 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0002_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20),
        ),
        migrations.AddField(
            model_name='individual',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20),
        ),
    ]