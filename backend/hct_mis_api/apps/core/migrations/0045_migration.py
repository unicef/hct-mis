# Generated by Django 3.2.12 on 2022-03-17 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flexibleattribute',
            name='type',
            field=models.CharField(choices=[('DATE', 'Date'), ('DECIMAL', 'Decimal'), ('IMAGE', 'Image'), ('INTEGER', 'Integer'), ('GEOPOINT', 'Geopoint'), ('SELECT_ONE', 'Select One'), ('SELECT_MANY', 'Select Many'), ('STRING', 'String')], max_length=16),
        ),
        migrations.AlterField(
            model_name='xlsxkobotemplate',
            name='status',
            field=models.CharField(choices=[('CONNECTION_FAILED', 'Connection failed'), ('PROCESSING', 'Processing'), ('SUCCESSFUL', 'Successful'), ('UNSUCCESSFUL', 'Unsuccessful'), ('UPLOADED', 'Uploaded')], max_length=200),
        ),
    ]
