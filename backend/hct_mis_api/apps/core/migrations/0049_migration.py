# Generated by Django 3.2.13 on 2022-07-20 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessarea',
            name='approval_number_required',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='authorization_number_required',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='finance_review_number_required',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
