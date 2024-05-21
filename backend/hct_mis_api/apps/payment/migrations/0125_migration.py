# Generated by Django 3.2.25 on 2024-04-21 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0124_migration'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='paymentplan',
            name='name_unique_per_program',
        ),
        migrations.AddConstraint(
            model_name='paymentplan',
            constraint=models.UniqueConstraint(condition=models.Q(('is_removed', False)), fields=('name', 'program', 'is_removed'), name='name_unique_per_program'),
        ),
    ]
