# Generated by Django 3.2.20 on 2023-08-02 10:34

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0068_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='MigrationStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_running', models.BooleanField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
