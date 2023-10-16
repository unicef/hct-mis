# Generated by Django 3.2.20 on 2023-09-26 10:13

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0158_migration'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='document',
            name='unique_for_individual_if_not_removed_and_valid',
        ),
        migrations.RemoveConstraint(
            model_name='document',
            name='unique_if_not_removed_and_valid',
        ),
        migrations.AddConstraint(
            model_name='document',
            constraint=models.UniqueConstraint(condition=models.Q(models.Q(('is_removed', False), ('status', 'VALID'), django.db.models.expressions.Func(django.db.models.expressions.F('type_id'), django.db.models.expressions.Value(True), function='check_unique_document_for_individual', output_field=models.BooleanField()))), fields=('type', 'country', 'program'), name='unique_for_individual_if_not_removed_and_valid'),
        ),
        migrations.AddConstraint(
            model_name='document',
            constraint=models.UniqueConstraint(condition=models.Q(models.Q(('is_removed', False), ('status', 'VALID'), django.db.models.expressions.Func(django.db.models.expressions.F('type_id'), django.db.models.expressions.Value(False), function='check_unique_document_for_individual', output_field=models.BooleanField()))), fields=('document_number', 'type', 'country', 'program'), name='unique_if_not_removed_and_valid'),
        ),
    ]
