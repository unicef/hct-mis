# Generated by Django 3.2.25 on 2024-07-18 18:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0049_migration'),
        ('targeting', '0044_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetpopulation',
            name='program_cycle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='target_populations', to='program.programcycle'),
        ),
    ]
