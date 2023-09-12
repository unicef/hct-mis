# Generated by Django 3.2.20 on 2023-09-04 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0038_migration'),
        ('accountability', '0007_migration'),
        ('targeting', '0039_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='program.program'),
        ),
    ]
