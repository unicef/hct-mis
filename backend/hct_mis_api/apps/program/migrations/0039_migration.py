# Generated by Django 3.2.20 on 2023-09-15 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_migration'),
        ('program', '0038_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='data_collecting_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='programs', to='core.datacollectingtype'),
        ),
    ]
