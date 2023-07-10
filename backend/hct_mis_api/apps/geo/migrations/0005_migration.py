# Generated by Django 2.2.16 on 2021-09-27 14:07

from django.db import migrations, models

MODELS = (
    "grievance.GrievanceTicket",
    "household.Household",
    "program.Program",
    "reporting.DashboardReport",
    "reporting.Report",
)


def copy_admin_area_data(apps, schema_editor):
    Area = apps.get_model("geo", "Area")
    areas = {}

    for model in MODELS:
        Model = apps.get_model(*model.split("."))
        try:
            for field in Model._meta.get_fields():
                if type(field) == models.ForeignKey:
                    opts = field.related_model._meta
                    if opts.app_label == "geo" and opts.model_name == "area":
                        old_field_name = field.name[:-4]
                        geo_name = field.name
                        records = Model.objects.all()
                        for record in records:
                            source = getattr(record, old_field_name)
                            if source:
                                p_code = source.p_code
                                if p_code not in areas.keys():
                                    areas[p_code] = Area.objects.get(p_code=p_code)
                                setattr(record, geo_name, areas[p_code])
                        Model.objects.bulk_update(records, [geo_name])
        except Exception:
            raise


class Migration(migrations.Migration):
    dependencies = [
        ("geo", "0004_migration"),
        ("grievance", "0001_migration_squashed_0034_migration"),
        ("household", "0087_migration"),
        ("program", "0029_migration"),
        ("reporting", "0008_migration_squashed_0014_migration"),
    ]

    operations = [migrations.RunPython(copy_admin_area_data, migrations.RunPython.noop)]
