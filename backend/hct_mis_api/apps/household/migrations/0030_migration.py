# Generated by Django 2.2.16 on 2020-11-12 19:53

from django.db import migrations

def fix_marital_status(apps, schema_editor):
    Individual = apps.get_model("household", "Individual")
    Individual.objects.filter(marital_status="WIDOW").update(marital_status="WIDOWED")

def empty_reverse(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('household', '0029_migration'),
    ]


    operations = [
        migrations.RunPython(fix_marital_status, empty_reverse),
    ]
