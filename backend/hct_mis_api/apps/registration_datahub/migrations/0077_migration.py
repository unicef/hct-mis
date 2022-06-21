# Generated by Django 3.2.13 on 2022-06-21 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_datahub', '0076_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diiaindividual',
            name='disability',
            field=models.CharField(blank=True, choices=[('True', 'disabled'), ('False', 'not disabled')], default='not disabled', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='diiaindividual',
            name='relationship',
            field=models.CharField(blank=True, choices=[(None, 'Unknown'), ('HEAD', 'Head of household (self)'), ('SON', 'Son'), ('DAUGHTER', 'Daughter'), ('HUSBAND', 'Husband'), ('WIFE', 'Wife')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='importedindividual',
            name='deduplication_golden_record_status',
            field=models.CharField(blank=True, choices=[('DUPLICATE', 'Duplicate'), ('NEEDS_ADJUDICATION', 'Needs Adjudication'), ('NOT_PROCESSED', 'Not Processed'), ('POSTPONE', 'Postpone'), ('UNIQUE', 'Unique')], default='UNIQUE', max_length=50),
        ),
    ]
