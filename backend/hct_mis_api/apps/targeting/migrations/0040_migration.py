# Generated by Django 3.2.20 on 2023-08-28 17:00

import django.contrib.postgres.fields.citext
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targeting', '0039_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetpopulation',
            name='name',
            field=django.contrib.postgres.fields.citext.CICharField(db_index=True, max_length=255, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255), django.core.validators.RegexValidator('\\s{2,}', 'Double spaces characters are not allowed.', code='double_spaces_characters_not_allowed', inverse_match=True), django.core.validators.RegexValidator('(^\\s+)|(\\s+$)', 'Leading or trailing spaces characters are not allowed.', code='leading_trailing_spaces_characters_not_allowed', inverse_match=True), django.core.validators.ProhibitNullCharactersValidator()]),
        ),
        migrations.AlterUniqueTogether(
            name='targetpopulation',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='targetpopulation',
            constraint=models.UniqueConstraint(condition=models.Q(('is_removed', False)), fields=('name', 'business_area', 'program', 'is_removed'), name='target_population_unique_if_not_removed'),
        ),
    ]
