# Generated by Django 3.2.13 on 2022-08-10 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steficon', '0011_migration_squashed_0016_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='type',
            field=models.CharField(choices=[('PAYMENT_PLAN', 'Payment Plan'), ('TARGETING', 'Targeting')], default='TARGETING', help_text='Use Rule for Targeting or Payment Plan', max_length=50),
        ),
    ]
