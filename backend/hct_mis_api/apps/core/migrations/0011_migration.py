# Generated by Django 2.2.16 on 2021-01-21 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminarea',
            name='admin_area_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_areas', to='core.AdminAreaLevel', verbose_name='Location Type'),
        ),
    ]
