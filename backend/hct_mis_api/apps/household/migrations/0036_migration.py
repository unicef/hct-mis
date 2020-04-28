# Generated by Django 2.2.8 on 2020-04-28 11:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0035_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='HouseholdIdentity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_number', models.CharField(max_length=255)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='households_identities', to='household.Agency')),
                ('household', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identities', to='household.Household')),
            ],
        ),
        migrations.CreateModel(
            name='IndividualIdentity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=255)),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='individual_identities', to='household.Agency')),
                ('individual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identities', to='household.Individual')),
            ],
            options={
                'unique_together': {('agency', 'number')},
            },
        ),
        migrations.DeleteModel(
            name='Identity',
        ),
    ]
