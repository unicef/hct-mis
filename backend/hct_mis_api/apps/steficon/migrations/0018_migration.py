# Generated by Django 3.2.15 on 2023-02-01 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steficon', '0017_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='language',
            field=models.CharField(choices=[('python', 'Python')], default='python', max_length=10),
        ),
        migrations.AlterField(
            model_name='rulecommit',
            name='language',
            field=models.CharField(choices=[('python', 'Python')], default='python', max_length=10),
        ),
    ]
