# Generated by Django 3.2.25 on 2024-08-07 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0047_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='biometric_deduplication_enabled',
            field=models.BooleanField(default=False, help_text='Enable Deduplication of Face Images'),
        ),
        migrations.AddField(
            model_name='program',
            name='deduplication_set_id',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='biometric_deduplication_threshold',
            field=models.FloatField(default=90.0, help_text='Threshold for Face Image Deduplication'),
        ),
    ]
