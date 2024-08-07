# Generated by Django 3.2.25 on 2024-06-21 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0178_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingDocument',
            fields=[
            ],
            options={
                'verbose_name': 'Imported Document',
                'verbose_name_plural': 'Imported Documents',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('household.document',),
        ),
        migrations.CreateModel(
            name='PendingHousehold',
            fields=[
            ],
            options={
                'verbose_name': 'Imported Household',
                'verbose_name_plural': 'Imported Households',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('household.household',),
        ),
        migrations.CreateModel(
            name='PendingIndividual',
            fields=[
            ],
            options={
                'verbose_name': 'Imported Individual',
                'verbose_name_plural': 'Imported Individuals',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('household.individual',),
        ),
        migrations.CreateModel(
            name='PendingIndividualIdentity',
            fields=[
            ],
            options={
                'verbose_name': 'Imported Individual Identity',
                'verbose_name_plural': 'Imported Individual Identities',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('household.individualidentity',),
        ),
        migrations.CreateModel(
            name='PendingIndividualRoleInHousehold',
            fields=[
            ],
            options={
                'verbose_name': 'Imported Individual Role In Household',
                'verbose_name_plural': 'Imported Individual Roles In Household',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('household.individualroleinhousehold',),
        ),
    ]
