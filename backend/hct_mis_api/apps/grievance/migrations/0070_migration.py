# Generated by Django 3.2.23 on 2024-02-26 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0062_migration_squashed_0069_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grievanceticket',
            name='is_original',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
