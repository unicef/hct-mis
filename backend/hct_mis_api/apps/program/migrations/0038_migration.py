# Generated by Django 3.2.15 on 2023-01-20 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0043_migration'),
        ('program', '0037_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='eligible_household_program_population_size',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='program',
            name='household_program_population_size',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='program',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='programs', to='account.partner'),
        ),
    ]
