# Generated by Django 2.2.16 on 2021-02-16 12:47

import django.contrib.postgres.fields.citext
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0052_migration'),
        ('steficon', '0002_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='household',
            name='address',
            field=django.contrib.postgres.fields.citext.CICharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='household',
            name='unicef_id',
            field=django.contrib.postgres.fields.citext.CICharField(blank=True, default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='individual',
            name='family_name',
            field=django.contrib.postgres.fields.citext.CICharField(blank=True, max_length=85),
        ),
        migrations.AlterField(
            model_name='individual',
            name='full_name',
            field=django.contrib.postgres.fields.citext.CICharField(max_length=255, validators=[django.core.validators.MinLengthValidator(2)]),
        ),
        migrations.AlterField(
            model_name='individual',
            name='given_name',
            field=django.contrib.postgres.fields.citext.CICharField(blank=True, max_length=85),
        ),
        migrations.AlterField(
            model_name='individual',
            name='middle_name',
            field=django.contrib.postgres.fields.citext.CICharField(blank=True, max_length=85),
        ),
        migrations.AlterField(
            model_name='individual',
            name='unicef_id',
            field=django.contrib.postgres.fields.citext.CICharField(blank=True, max_length=250),
        ),
    ]
