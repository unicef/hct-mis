# Generated by Django 2.2.16 on 2021-09-27 12:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0004_migration'),
        ('household', '0003_migration_squashed_0086_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='admin_area_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='geo.Area'),
        ),
    ]