# Generated by Django 2.2.8 on 2020-10-26 11:22

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import hct_mis_api.apps.targeting.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('targeting', '0010_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='targetingcriteriarulefilter',
            name='head_of_household',
        ),
        migrations.CreateModel(
            name='TargetingIndividualRuleFilterBlock',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('targeting_criteria_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individuals_filters_blocks', to='targeting.TargetingCriteriaRule')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, hct_mis_api.apps.targeting.models.TargetingIndividualRuleFilterBlockMixin),
        ),
        migrations.CreateModel(
            name='TargetingIndividualBlockRuleFilter',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comparision_method', models.CharField(choices=[('EQUALS', 'Equals'), ('NOT_EQUALS', 'Not Equals'), ('CONTAINS', 'Contains'), ('NOT_CONTAINS', 'Does not contain'), ('RANGE', 'In between <>'), ('NOT_IN_RANGE', 'Not in between <>'), ('GREATER_THAN', 'Greater than'), ('LESS_THAN', 'Less than')], max_length=20)),
                ('is_flex_field', models.BooleanField(default=False)),
                ('field_name', models.CharField(max_length=50)),
                ('arguments', django.contrib.postgres.fields.jsonb.JSONField(help_text='\n            Array of arguments\n            ')),
                ('individuals_filters_block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individual_block_filters', to='targeting.TargetingIndividualRuleFilterBlock')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, hct_mis_api.apps.targeting.models.TargetingCriteriaFilterMixin),
        ),
    ]
