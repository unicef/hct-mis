# Generated by Django 3.2.15 on 2022-10-18 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0124_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='family_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
