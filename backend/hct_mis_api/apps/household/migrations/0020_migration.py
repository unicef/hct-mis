# Generated by Django 2.2.8 on 2020-04-23 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0019_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='household',
            name='admin_area',
        ),
        migrations.AlterField(
            model_name='individual',
            name='estimated_birth_date',
            field=models.DateField(blank=True, choices=[('YES', 'Yes'), ('NO', 'No')], null=True),
        ),
    ]
