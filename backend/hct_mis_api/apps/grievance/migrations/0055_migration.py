# Generated by Django 3.2.15 on 2022-09-12 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0054_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grievanceticket',
            name='sub_category',
        ),
    ]
