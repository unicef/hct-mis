# Generated by Django 2.2.16 on 2021-06-29 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0038_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importedindividual',
            name='disability',
            field=models.CharField(choices=[('disabled', 'disabled'), ('not disabled', 'not disabled')], default='not disabled', max_length=20),
        ),
    ]
