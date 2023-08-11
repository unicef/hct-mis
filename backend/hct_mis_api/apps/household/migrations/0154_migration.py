# Generated by Django 3.2.18 on 2023-06-29 21:55
import logging

import django.db.models.deletion
from django.db import migrations, models

logger = logging.getLogger(__name__)


def _batch_create_collections(representation_model, collection_model, related_name, representations) -> None:
    # Create HouseholdCollection/IndividualCollection objects for every Household/Individual object
    collections = collection_model.objects.bulk_create([collection_model() for _ in representations])

    # Prepare a list of Household/Individual objects with corresponding HouseholdCollection/IndividualCollection objects
    representations_with_collection = [
        representation_model(**{"id": representation.id, related_name: collection})
        for representation, collection in zip(representations, collections)
    ]
    representation_model.objects.bulk_update(representations_with_collection, [related_name])


def _create_collections(representation_model, collection_model, related_name, business_area_model):
    batch_size = 500
    for business_area in business_area_model.objects.all():
        logger.info(f"Starting batch collection creation for business area: {business_area.name}")
        total_representations = representation_model.objects.filter(business_area=business_area).count()
        all_representations = representation_model.objects.filter(business_area=business_area).all()

        for batch_start in range(0, total_representations, batch_size):
            batch_end = batch_start + batch_size
            representations = all_representations[batch_start:batch_end]
            _batch_create_collections(representation_model, collection_model, related_name, representations)
        logger.info(f"Finished batch collection creation for business area: {business_area.name}")


def create_hh_and_ind_collections(apps, schema_editor):
    # Create representation collection for every household and individual already present in db
    Household = apps.get_model('household', 'Household')
    HouseholdCollection = apps.get_model('household', 'HouseholdCollection')
    Individual = apps.get_model('household', 'Individual')
    IndividualCollection = apps.get_model('household', 'IndividualCollection')
    BusinessArea = apps.get_model('core', 'BusinessArea')

    _create_collections(Household, HouseholdCollection, "household_collection", BusinessArea)
    _create_collections(Individual, IndividualCollection, "individual_collection", BusinessArea)


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0153_migration'),
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
            model_name='household',
            name='household_collection',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='households',
                to='household.HouseholdCollection',
            ),
        ),
        migrations.AddField(
            model_name='individual',
            name='individual_collection',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='individuals',
                to='household.IndividualCollection',
            ),
        ),
        migrations.RunPython(create_hh_and_ind_collections, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='household',
            name='household_collection',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='households',
                to='household.HouseholdCollection',
            ),
        ),
        migrations.AlterField(
            model_name='individual',
            name='individual_collection',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='individuals',
                to='household.IndividualCollection',
            ),
        ),
    ]
