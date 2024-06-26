# Generated by Django 2.2.16 on 2021-10-14 10:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0087_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='household',
            options={'permissions': (('can_withdrawn', 'Can withdrawn Household'),), 'verbose_name': 'Household'},
        ),
        migrations.RenameField(
            model_name='household',
            old_name='female_age_group_0_4_count',
            new_name='female_age_group_0_5_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='female_age_group_0_4_disabled_count',
            new_name='female_age_group_0_5_disabled_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='female_age_group_13_17_count',
            new_name='female_age_group_12_17_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='female_age_group_13_17_disabled_count',
            new_name='female_age_group_12_17_disabled_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='female_age_group_5_12_count',
            new_name='female_age_group_6_11_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='female_age_group_5_12_disabled_count',
            new_name='female_age_group_6_11_disabled_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='male_age_group_0_4_count',
            new_name='male_age_group_0_5_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='male_age_group_0_4_disabled_count',
            new_name='male_age_group_0_5_disabled_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='male_age_group_13_17_count',
            new_name='male_age_group_12_17_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='male_age_group_13_17_disabled_count',
            new_name='male_age_group_12_17_disabled_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='male_age_group_5_12_count',
            new_name='male_age_group_6_11_count',
        ),
        migrations.RenameField(
            model_name='household',
            old_name='male_age_group_5_12_disabled_count',
            new_name='male_age_group_6_11_disabled_count',
        ),
    ]
