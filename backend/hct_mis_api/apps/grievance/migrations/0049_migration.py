# Generated by Django 3.2.13 on 2022-07-28 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0048_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='grievanceticket',
            name='postpone_deduplication',
            field=models.BooleanField(default=False),
        ),
    ]
