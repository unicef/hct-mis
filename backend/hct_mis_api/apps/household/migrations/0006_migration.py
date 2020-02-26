# Generated by Django 2.2.8 on 2020-02-24 16:02

import django.core.validators
from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0005_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='individual',
            name='disability',
            field=models.CharField(choices=[('NO', 'No'), ('SEEING', 'Difficulty seeing (even if wearing glasses)'), ('HEARING', 'Difficulty hearing (even if using a hearing aid)'), ('WALKING', 'Difficulty walking or climbing steps'), ('MEMORY', 'Difficulty remembering or concentrating'), ('SELF_CARE', 'Difficulty with self care (washing, dressing)'), ('COMMUNICATING', 'Difficulty communicating (e.g understanding or being understood)')], default='NO', max_length=3),
        ),
        migrations.AddField(
            model_name='individual',
            name='middle_name',
            field=models.CharField(blank=True, max_length=85, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(85)]),
        ),
        migrations.AddField(
            model_name='individual',
            name='phone_number_alternative',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None),
        ),
        migrations.AddField(
            model_name='individual',
            name='work_status',
            field=models.CharField(choices=[('YES', 'Yes'), ('NO', 'No')], default='NO', max_length=3),
        ),
        migrations.AlterField(
            model_name='household',
            name='family_size',
            field=models.PositiveIntegerField(default=4),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='individual',
            name='first_name',
            field=models.CharField(max_length=85, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(85)]),
        ),
        migrations.AlterField(
            model_name='individual',
            name='last_name',
            field=models.CharField(max_length=85, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(85)]),
        ),
        migrations.AlterField(
            model_name='registrationdataimport',
            name='import_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
