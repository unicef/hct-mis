# Generated by Django 3.2.19 on 2023-07-12 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0038_migration'),
        ('activity_log', '0005_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='logentry',
            name='program',
        ),
        migrations.AddField(
            model_name='logentry',
            name='programs',
            field=models.ManyToManyField(blank=True, related_name='activity_logs', to='program.Program'),
        ),
    ]
