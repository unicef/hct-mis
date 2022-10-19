# Generated by Django 3.2.15 on 2022-10-19 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='storagefile',
            name='status',
            field=models.CharField(choices=[('Not processed', 'Not processed'), ('Processing', 'Processing'), ('Finished', 'Finished'), ('Failed', 'Failed')], default='Not processed', max_length=25),
        ),
        migrations.AlterField(
            model_name='storagefile',
            name='file',
            field=models.FileField(upload_to='files'),
        ),
    ]
