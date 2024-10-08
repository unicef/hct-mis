# Generated by Django 3.2.25 on 2024-08-13 07:06

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0049_migration'),
        ('household', '0184_migration'),
        ('registration_data', '0037_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationdataimport',
            name='deduplication_engine_status',
            field=models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('UPLOADED', 'Uploaded'), ('IN_PROGRESS', 'In Progress'), ('FINISHED', 'Finished'), ('ERROR', 'Error'), ('UPLOAD_ERROR', 'Upload Error')], default=None, max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='DeduplicationEngineSimilarityPair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('similarity_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('individual1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='biometric_duplicates_1', to='household.individual')),
                ('individual2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='biometric_duplicates_2', to='household.individual')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deduplication_engine_similarity_pairs', to='program.program')),
            ],
        ),
        migrations.AddConstraint(
            model_name='deduplicationenginesimilaritypair',
            constraint=models.CheckConstraint(check=models.Q(('individual1__lt', django.db.models.expressions.F('individual2'))), name='individual1_lt_individual2'),
        ),
        migrations.AlterUniqueTogether(
            name='deduplicationenginesimilaritypair',
            unique_together={('individual1', 'individual2')},
        ),
        migrations.AddField(
            model_name='registrationdataimport',
            name='dedup_engine_batch_duplicates',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='registrationdataimport',
            name='dedup_engine_golden_record_duplicates',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
