# Generated by Django 3.2.19 on 2023-06-11 10:42

import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


def empty_reverse(apps, schema_editor):
    pass
def remove_duplicates(apps, schema_editor):
    AdminAreaLevel = apps.get_model("core", "AdminAreaLevel")
    levels_without_ids = AdminAreaLevel.objects.filter(datamart_id__isnull=True)
    for level in levels_without_ids:
        new_datamart_id = level.admin_level
        duplicated = AdminAreaLevel.objects.filter(datamart_id=new_datamart_id)
        duplicated.delete()
        level.datamart_id=new_datamart_id
        level.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_migration_squashed_0016_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='countrycodemap',
            options={'ordering': ('country',)},
        ),
        migrations.AlterField(
            model_name='adminarea',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='adminarea',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='adminarealevel',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='adminarealevel',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='businessarea',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='businessarea',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='flexibleattribute',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='flexibleattribute',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='flexibleattributechoice',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='flexibleattributechoice',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='flexibleattributegroup',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='flexibleattributegroup',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='xlsxkobotemplate',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='xlsxkobotemplate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AddField(
            model_name='xlsxkobotemplate',
            name='first_connection_failed_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='businessarea',
            name='rapid_pro_api_key',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='businessarea',
            name='rapid_pro_host',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='xlsxkobotemplate',
            name='status',
            field=models.CharField(choices=[('SUCCESSFUL', 'Successful'), ('UPLOADED', 'Successful'), ('UNSUCCESSFUL', 'Unsuccessful'), ('PROCESSING', 'Processing'), ('CONNECTION_FAILED', 'Connection failed')], max_length=200),
        ),
        migrations.AlterField(
            model_name='flexibleattribute',
            name='type',
            field=models.CharField(choices=[('STRING', 'String'), ('IMAGE', 'Image'), ('INTEGER', 'Integer'), ('DECIMAL', 'Decimal'), ('SELECT_ONE', 'Select One'), ('SELECT_MANY', 'Select Many'), ('DATE', 'Date'), ('GEOPOINT', 'Geopoint')], max_length=16),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='is_split',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='core.businessarea'),
        ),
        migrations.AddField(
            model_name='adminarealevel',
            name='area_code',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='adminarea',
            name='p_code',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='P Code'),
        ),
        migrations.AlterUniqueTogether(
            name='adminarealevel',
            unique_together={('area_code', 'admin_level')},
        ),
        migrations.RemoveField(
            model_name='adminarealevel',
            name='business_area',
        ),
        migrations.AddField(
            model_name='adminarealevel',
            name='datamart_id',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
        migrations.RemoveField(
            model_name='adminarealevel',
            name='real_admin_level',
        ),
        migrations.AddField(
            model_name='adminarealevel',
            name='country_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='adminarealevel',
            name='name',
            field=models.CharField(max_length=64, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='adminarealevel',
            name='admin_level',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Admin Level'),
        ),
        migrations.AlterUniqueTogether(
            name='adminarealevel',
            unique_together={('country_name', 'admin_level')},
        ),
        migrations.AddField(
            model_name='businessarea',
            name='countries',
            field=models.ManyToManyField(blank=True, limit_choices_to={'admin_level': 0}, to='core.AdminAreaLevel'),
        ),
        migrations.AddField(
            model_name='adminarealevel',
            name='business_area',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_area_level', to='core.businessarea'),
        ),
        migrations.AddField(
            model_name='adminarealevel',
            name='country',
            field=models.ForeignKey(blank=True, limit_choices_to={'admin_level': 0}, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.adminarealevel'),
        ),
        migrations.AlterField(
            model_name='businessarea',
            name='countries',
            field=models.ManyToManyField(blank=True, limit_choices_to={'admin_level': 0}, related_name='business_areas', to='core.AdminAreaLevel'),
        ),
        migrations.AlterUniqueTogether(
            name='adminarealevel',
            unique_together={('country', 'admin_level')},
        ),
        migrations.RunPython(remove_duplicates, empty_reverse),
        migrations.AlterModelOptions(
            name='adminarea',
            options={'ordering': ['title'], 'permissions': (('import_from_csv', 'Import AdminAreas from CSV file'), ('load_from_datamart', 'Load data from Datamart'))},
        ),
        migrations.AlterModelOptions(
            name='adminarealevel',
            options={'ordering': ['name'], 'permissions': (('load_from_datamart', 'Load data from Datamart'), ('can_sync_with_ad', 'Can synchronise user with ActiveDirectory'), ('can_upload_to_kobo', 'Can upload users to Kobo')), 'verbose_name': 'Admin Area Level'},
        ),
        migrations.AlterModelOptions(
            name='businessarea',
            options={'ordering': ['name'], 'permissions': (('can_split', 'Can split BusinessArea'),)},
        ),
        migrations.AlterField(
            model_name='adminarealevel',
            name='business_area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_area_level', to='core.businessarea'),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='deduplication_batch_duplicate_score',
            field=models.FloatField(default=6.0, help_text='Results equal or above this score are considered duplicates', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='deduplication_batch_duplicates_allowed',
            field=models.IntegerField(default=5, help_text='If amount of duplicates for single individual exceeds this limit deduplication is aborted'),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='deduplication_batch_duplicates_percentage',
            field=models.IntegerField(default=50, help_text='If percentage of duplicates is higher or equal to this setting, deduplication is aborted'),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='deduplication_golden_record_duplicate_score',
            field=models.FloatField(default=6.0, help_text='Results equal or above this score are considered duplicates', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='deduplication_golden_record_duplicates_allowed',
            field=models.IntegerField(default=5, help_text='If amount of duplicates for single individual exceeds this limit deduplication is aborted'),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='deduplication_golden_record_duplicates_percentage',
            field=models.IntegerField(default=50, help_text='If percentage of duplicates is higher or equal to this setting, deduplication is aborted'),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='deduplication_golden_record_min_score',
            field=models.FloatField(default=11.0, help_text='Results below the minimum score will not be taken into account', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='custom_fields',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterModelOptions(
            name='businessarea',
            options={'ordering': ['name'], 'permissions': (('can_split', 'Can split BusinessArea'), ('can_send_doap', 'Can send DOAP matrix'), ('can_reset_doap', 'Can force sync DOAP matrix'), ('can_export_doap', 'Can export DOAP matrix'))},
        ),
        migrations.RenameField(
            model_name='businessarea',
            old_name='deduplication_batch_duplicate_score',
            new_name='deduplication_duplicate_score',
        ),
        migrations.RemoveField(
            model_name='businessarea',
            name='deduplication_golden_record_duplicate_score',
        ),
        migrations.RemoveField(
            model_name='businessarea',
            name='deduplication_golden_record_min_score',
        ),
        migrations.AddField(
            model_name='businessarea',
            name='deduplication_possible_duplicate_score',
            field=models.FloatField(default=6.0, help_text='Results equal or above this score are considered possible duplicates (needs adjudication) must be lower than deduplication_duplicate_score', validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AddField(
            model_name='businessarea',
            name='screen_beneficiary',
            field=models.BooleanField(default=False),
        ),
    ]
