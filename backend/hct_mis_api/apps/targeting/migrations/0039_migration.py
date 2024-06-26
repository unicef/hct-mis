# Generated by Django 3.2.18 on 2023-05-26 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targeting', '0038_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetingcriteria',
            name='flag_exclude_if_active_adjudication_ticket',
            field=models.BooleanField(default=False, help_text='Exclude households with individuals (members or collectors) that have active adjudication ticket(s).'),
        ),
        migrations.AddField(
            model_name='targetingcriteria',
            name='flag_exclude_if_on_sanction_list',
            field=models.BooleanField(default=False, help_text='Exclude households with individuals (members or collectors) on sanction list.'),
        ),
    ]
