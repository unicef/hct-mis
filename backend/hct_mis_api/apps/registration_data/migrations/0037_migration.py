# Generated by Django 3.2.25 on 2024-06-04 20:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0177_migration'),
        ('registration_data', '0036_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='koboimportedsubmission',
            name='imported_household',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='household.household'),
        ),
    ]
