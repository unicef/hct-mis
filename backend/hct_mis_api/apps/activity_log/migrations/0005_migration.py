# Generated by Django 3.2.20 on 2023-09-04 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0038_migration'),
        ('activity_log', '0001_migration_squashed_0004_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='logentry',
            name='programs',
            field=models.ManyToManyField(blank=True, related_name='activity_logs', to='program.Program'),
        ),
    ]
