# Generated by Django 3.2.15 on 2022-10-21 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0050_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grievanceticket',
            name='unicef_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]
