# Generated by Django 2.2.16 on 2021-12-10 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0091_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='row_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='kobo_asset_id',
            field=models.CharField(blank=True, default='', max_length=150),
        ),
        migrations.AddField(
            model_name='individual',
            name='row_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
