# Generated by Django 2.2.16 on 2021-09-16 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0003_migration'),
        ('sanction_list', '0001_migration_squashed_0009_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='sanctionlistindividual',
            name='country_of_birth_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='geo.Country'),
        ),
        migrations.AddField(
            model_name='sanctionlistindividualcountries',
            name='country_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='geo.Country'),
        ),
        migrations.AddField(
            model_name='sanctionlistindividualdocument',
            name='issuing_country_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='geo.Country'),
        ),
        migrations.AddField(
            model_name='sanctionlistindividualnationalities',
            name='nationality_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='geo.Country'),
        ),
    ]
