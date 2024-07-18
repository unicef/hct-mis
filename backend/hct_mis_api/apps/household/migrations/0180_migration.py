# Generated by Django 3.2.25 on 2024-06-21 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0179_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccountinfo',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10),
        ),
        migrations.AlterField(
            model_name='document',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10),
        ),
        migrations.AlterField(
            model_name='household',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10),
        ),
        migrations.AlterField(
            model_name='individual',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10),
        ),
        migrations.AlterField(
            model_name='individualidentity',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10),
        ),
        migrations.AlterField(
            model_name='individualroleinhousehold',
            name='rdi_merge_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('MERGED', 'Merged')], default='PENDING', max_length=10),
        ),
    ]
