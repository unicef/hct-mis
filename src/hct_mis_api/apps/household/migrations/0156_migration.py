# Generated by Django 3.2.20 on 2023-09-18 12:27

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0039_migration'),
        ('household', '0155_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='HouseholdCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unicef_id', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IndividualCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unicef_id', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='bankaccountinfo',
            name='copied_from',
            field=models.ForeignKey(blank=True, help_text='If this object was copied from another, this field will contain the object it was copied from.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='copied_to', to='household.bankaccountinfo'),
        ),
        migrations.AddField(
            model_name='bankaccountinfo',
            name='is_migration_handled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bankaccountinfo',
            name='is_original',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='document',
            name='copied_from',
            field=models.ForeignKey(blank=True, help_text='If this object was copied from another, this field will contain the object it was copied from.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='copied_to', to='household.document'),
        ),
        migrations.AddField(
            model_name='document',
            name='is_migration_handled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='document',
            name='is_original',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='document',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='program.program'),
        ),
        migrations.AddField(
            model_name='entitlementcard',
            name='is_original',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='household',
            name='copied_from',
            field=models.ForeignKey(blank=True, help_text='If this household was copied from another household, this field will contain the household it was copied from.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='copied_to', to='household.household'),
        ),
        migrations.AddField(
            model_name='household',
            name='is_migration_handled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='household',
            name='is_original',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='household',
            name='origin_unicef_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='program.program'),
        ),
        migrations.AddField(
            model_name='individual',
            name='copied_from',
            field=models.ForeignKey(blank=True, help_text='If this individual was copied from another individual, this field will contain the individual it was copied from.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='copied_to', to='household.individual'),
        ),
        migrations.AddField(
            model_name='individual',
            name='is_migration_handled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='individual',
            name='is_original',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='origin_unicef_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='individuals', to='program.program'),
        ),
        migrations.AddField(
            model_name='individualidentity',
            name='copied_from',
            field=models.ForeignKey(blank=True, help_text='If this object was copied from another, this field will contain the object it was copied from.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='copied_to', to='household.individualidentity'),
        ),
        migrations.AddField(
            model_name='individualidentity',
            name='created',
            field=model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created'),
        ),
        migrations.AddField(
            model_name='individualidentity',
            name='is_migration_handled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='individualidentity',
            name='is_original',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='individualidentity',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='individualidentity',
            name='modified',
            field=model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified'),
        ),
        migrations.AddField(
            model_name='individualroleinhousehold',
            name='copied_from',
            field=models.ForeignKey(blank=True, help_text='If this object was copied from another, this field will contain the object it was copied from.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='copied_to', to='household.individualroleinhousehold'),
        ),
        migrations.AddField(
            model_name='individualroleinhousehold',
            name='is_migration_handled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='individualroleinhousehold',
            name='is_original',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='individualroleinhousehold',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='household',
            name='household_collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='households', to='household.householdcollection'),
        ),
        migrations.AddField(
            model_name='individual',
            name='individual_collection',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='individuals', to='household.individualcollection'),
        ),
    ]
