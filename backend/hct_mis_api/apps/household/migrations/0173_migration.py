# Generated by Django 3.2.25 on 2024-03-22 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0046_migration'),
        ('household', '0172_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='xlsxupdatefile',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='program.program'),
        ),
    ]
