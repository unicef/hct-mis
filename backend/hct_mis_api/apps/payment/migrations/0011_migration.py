# Generated by Django 2.2.8 on 2020-07-21 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0010_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrecord',
            name='transaction_reference_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='paymentrecord',
            name='vision_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
