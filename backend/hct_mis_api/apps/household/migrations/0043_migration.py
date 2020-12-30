# Generated by Django 2.2.16 on 2020-12-29 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0042_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='household',
            name='collect_individual_data',
            field=models.CharField(choices=[('', 'None'), ('1', 'Yes'), ('0', 'No')], default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='individual',
            name='work_status',
            field=models.CharField(blank=True, choices=[('1', 'Yes'), ('0', 'No'), ('NOT_PROVIDED', 'Not provided')], default='NOT_PROVIDED', max_length=20),
        ),
    ]
