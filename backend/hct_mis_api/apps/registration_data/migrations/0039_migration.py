# Generated by Django 3.2.25 on 2024-06-21 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_data', '0038_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='importdata',
            name='delivery_mechanisms_validation_errors',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='importdata',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('RUNNING', 'Running'), ('FINISHED', 'Finished'), ('ERROR', 'Error'), ('VALIDATION_ERROR', 'Validation Error'), ('DELIVERY_MECHANISMS_VALIDATION_ERROR', 'Delivery Mechanisms Validation Error')], default='FINISHED', max_length=40),
        ),
    ]
