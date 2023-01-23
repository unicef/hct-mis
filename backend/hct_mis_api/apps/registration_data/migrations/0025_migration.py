# Generated by Django 3.2.15 on 2023-01-20 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('targeting', '0036_migration'),
        ('program', '0037_migration'),
        ('registration_data', '0024_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramCriteria',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('targeting.targetingcriteria',),
        ),
        migrations.AddField(
            model_name='registrationdataimport',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registration_data_imports', to='program.program'),
        ),
        migrations.AddField(
            model_name='registrationdataimport',
            name='program_criteria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registration_data_imports', to='registration_data.programcriteria'),
        ),
    ]
