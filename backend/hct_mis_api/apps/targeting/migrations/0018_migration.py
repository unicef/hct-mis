# Generated by Django 2.2.16 on 2021-02-16 13:11

import django.contrib.postgres.fields.citext
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('targeting', '0017_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='householdselection',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='householdselection',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetingcriteria',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetingcriteria',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetingcriteriarule',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetingcriteriarule',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetingcriteriarulefilter',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetingcriteriarulefilter',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetingindividualblockrulefilter',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetingindividualblockrulefilter',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetingindividualrulefilterblock',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetingindividualrulefilterblock',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetpopulation',
            name='ca_hash_id',
            field=django.contrib.postgres.fields.citext.CICharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='targetpopulation',
            name='ca_id',
            field=django.contrib.postgres.fields.citext.CICharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='targetpopulation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='targetpopulation',
            name='name',
            field=django.contrib.postgres.fields.citext.CICharField(db_index=True, max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='targetpopulation',
            name='sent_to_datahub',
            field=models.BooleanField(db_index=True, default=False, help_text='\n            Flag set when TP is processed by airflow task\n            '),
        ),
        migrations.AlterField(
            model_name='targetpopulation',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Open'), ('APPROVED', 'Closed'), ('FINALIZED', 'Sent')], db_index=True, default='DRAFT', max_length=256),
        ),
        migrations.AlterField(
            model_name='targetpopulation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
    ]
