# Generated by Django 3.2.24 on 2024-02-16 06:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def set_business_area(apps, schema_editor):
    BusinessArea = apps.get_model("core", "BusinessArea")
    afghanistan = BusinessArea.objects.filter(slug="afghanistan").first()
    if afghanistan is None:
        return
    TargetPopulation = apps.get_model("targeting", "TargetPopulation")
    TargetPopulation.objects.filter(business_area__isnull=True).update(
        business_area=afghanistan
    )


def set_business_area_2(apps, schema_editor):
    BusinessArea = apps.get_model("core", "BusinessArea")
    afghanistan = BusinessArea.objects.filter(slug="afghanistan").first()
    if afghanistan is None:
        return
    TargetPopulation = apps.get_model("targeting", "TargetPopulation")
    TargetPopulation.objects.filter(business_area__isnull=True).update(
        business_area=afghanistan
    )


class Migration(migrations.Migration):

    replaces = [('targeting', '0002_migration'), ('targeting', '0003_migration'), ('targeting', '0004_migration'), ('targeting', '0005_migration'), ('targeting', '0006_migration')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_migration_squashed_0006_migration'),
        ('targeting', '0001_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetingcriteriarulefilter',
            name='field_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AddField(
            model_name='targetpopulation',
            name='approved_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='targetpopulation',
            name='approved_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_target_populations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='targetpopulation',
            name='finalized_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='targetpopulation',
            name='finalized_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='finalized_target_populations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='targetpopulation',
            name='business_area',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.businessarea'),
        ),
        migrations.RunPython(set_business_area),
        migrations.AlterUniqueTogether(
            name='targetpopulation',
            unique_together={('name', 'business_area')},
        ),
        migrations.RunPython(set_business_area_2),
    ]
