# Generated by Django 3.2.19 on 2023-06-19 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0038_migration'),
        ('activity_log', '0001_migration_squashed_0004_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='logentry',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='program.program'),
        ),
    ]
