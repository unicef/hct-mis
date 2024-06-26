# Generated by Django 3.2.15 on 2022-11-28 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0122_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individual',
            name='deduplication_batch_status',
            field=models.CharField(choices=[('DUPLICATE_IN_BATCH', 'Duplicate in batch'), ('NOT_PROCESSED', 'Not Processed'), ('SIMILAR_IN_BATCH', 'Similar in batch'), ('UNIQUE_IN_BATCH', 'Unique in batch')], db_index=True, default='UNIQUE_IN_BATCH', max_length=50),
        ),
        migrations.AlterField(
            model_name='individual',
            name='deduplication_golden_record_status',
            field=models.CharField(choices=[('DUPLICATE', 'Duplicate'), ('NEEDS_ADJUDICATION', 'Needs Adjudication'), ('NOT_PROCESSED', 'Not Processed'), ('POSTPONE', 'Postpone'), ('UNIQUE', 'Unique')], db_index=True, default='UNIQUE', max_length=50),
        ),
        migrations.RunSQL("CREATE INDEX IF NOT EXISTS household_household_default_page_index ON public.household_household USING btree (created_at, business_area_id, is_removed) WHERE NOT is_removed;","DROP INDEX IF EXISTS household_household_default_page_index;")
    ]
