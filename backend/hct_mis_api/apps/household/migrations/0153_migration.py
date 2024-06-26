# Generated by Django 3.2.20 on 2023-08-02 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0152_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='registration_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Registration ID (Aurora)'),
        ),
        migrations.AddField(
            model_name='individual',
            name='registration_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Registration ID (Aurora)'),
        ),
    ]
