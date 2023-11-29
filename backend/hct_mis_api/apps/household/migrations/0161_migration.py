# Generated by Django 3.2.22 on 2023-11-21 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0160_migration'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE household_householdcollection ADD unicef_id_index SERIAL",
        ),
        migrations.RunSQL(
            sql="\n        CREATE OR REPLACE FUNCTION create_hhc_unicef_id() RETURNS trigger\n            LANGUAGE plpgsql\n            AS $$\n        begin\n          NEW.unicef_id := format('HHC-%s', trim(replace(to_char(NEW.unicef_id_index,'0000,0000'),',','.')));\n          return NEW;\n        end\n        $$;\n        ",
        ),
        migrations.RunSQL(
            sql="UPDATE household_householdcollection SET unicef_id = format('HHC-%s' ,trim(replace(to_char(unicef_id_index,'0000,0000'),',','.')))",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE household_individualcollection ADD unicef_id_index SERIAL",
        ),
        migrations.RunSQL(
            sql="\n        CREATE OR REPLACE FUNCTION create_indc_unicef_id() RETURNS trigger\n            LANGUAGE plpgsql\n            AS $$\n        begin\n          NEW.unicef_id := format('INDC-%s', trim(replace(to_char(NEW.unicef_id_index,'0000,0000'),',','.')));\n          return NEW;\n        end\n        $$;\n        ",
        ),
        migrations.RunSQL(
            sql="UPDATE household_individualcollection SET unicef_id = format('INDC-%s' ,trim(replace(to_char(unicef_id_index,'0000,0000'),',','.')))",
        ),
    ]
