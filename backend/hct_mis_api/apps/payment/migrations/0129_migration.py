# Generated by Django 3.2.25 on 2024-05-15 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0128_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='fsp_auth_code',
            field=models.CharField(blank=True, help_text='FSP Auth Code', max_length=128, null=True),
        ),
    ]
