# Generated by Django 3.2.23 on 2024-01-16 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0107_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diiaindividual',
            name='imported_individual',
        ),
        migrations.RemoveField(
            model_name='diiaindividual',
            name='registration_data_import',
        ),
        migrations.RemoveField(
            model_name='importedhousehold',
            name='diia_rec_id',
        ),
        migrations.AlterField(
            model_name='importdata',
            name='data_type',
            field=models.CharField(choices=[('XLSX', 'XLSX File'), ('JSON', 'JSON File'), ('FLEX', 'Flex Registration')], default='XLSX', max_length=4),
        ),
        migrations.DeleteModel(
            name='DiiaHousehold',
        ),
        migrations.DeleteModel(
            name='DiiaIndividual',
        ),
    ]
