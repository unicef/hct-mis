# Generated by Django 2.2.16 on 2021-02-10 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0046_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='household',
            name='status',
        ),
        migrations.RemoveField(
            model_name='individual',
            name='status',
        ),
        migrations.AddField(
            model_name='household',
            name='deactivated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='household',
            name='deactivated_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='duplicate',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='individual',
            name='duplicate_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='is_removed_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='withdrawn',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='individual',
            name='withdrawn_date',
            field=models.DateTimeField(null=True),
        ),
    ]
