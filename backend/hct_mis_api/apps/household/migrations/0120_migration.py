# Generated by Django 3.2.15 on 2022-10-20 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_migration_squashed_0057_migration'),
        ('household', '0119_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='family_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='storage_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.storagefile'),
        ),
    ]
