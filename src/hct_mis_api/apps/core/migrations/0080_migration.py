# Generated by Django 3.2.25 on 2024-07-15 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0079_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='periodicfielddata',
            name='subtype',
            field=models.CharField(choices=[('DATE', 'Date'), ('DECIMAL', 'Number'), ('STRING', 'Text'), ('BOOLEAN', 'Yes/No')], max_length=16),
        ),
    ]
