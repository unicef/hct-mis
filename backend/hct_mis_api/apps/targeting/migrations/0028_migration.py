# Generated by Django 2.2.16 on 2022-01-15 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targeting', '0027_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetpopulation',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Open'), ('LOCKED', 'Locked'), ('STEFICON_WAIT', 'Waiting for Rule Engine'), ('STEFICON_RUN', 'Rule Engine Running'), ('STEFICON_COMPLETED', 'Rule Engine Completed'), ('STEFICON_ERROR', 'Rule Engine Errored'), ('PROCESSING', 'Processing'), ('READY_FOR_CASH_ASSIST', 'Ready for cash assist')], db_index=True, default='DRAFT', max_length=256),
        ),
    ]
