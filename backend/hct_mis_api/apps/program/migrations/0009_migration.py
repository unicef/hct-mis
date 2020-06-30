# Generated by Django 2.2.8 on 2020-06-19 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0008_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='program',
            name='program_ca_id',
        ),
        migrations.AddField(
            model_name='program',
            name='ca_hash_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='ca_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='ca_hash_id',
            field=models.UUIDField(null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='cashplan',
            name='ca_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
