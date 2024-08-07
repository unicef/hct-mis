# Generated by Django 3.2.25 on 2024-08-01 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0081_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flexibleattribute',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AddConstraint(
            model_name='flexibleattribute',
            constraint=models.UniqueConstraint(fields=('name', 'program'), name='unique_name_program'),
        ),
        migrations.AddConstraint(
            model_name='flexibleattribute',
            constraint=models.UniqueConstraint(condition=models.Q(('program__isnull', True)), fields=('name',), name='unique_name_without_program'),
        ),
    ]
