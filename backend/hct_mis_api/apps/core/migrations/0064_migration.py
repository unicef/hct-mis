# Generated by Django 3.2.13 on 2022-08-16 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0063_migration"),
    ]

    operations = [
        migrations.RunSQL(
            """
            create or replace function payment_plan_business_area_for_old_ba(id text)
               returns text 
               language plpgsql
              as
            $$
            declare 
            -- variable declaration
            begin
                execute format('create sequence if not exists payment_plan_business_area_seq_%s', translate(id::text, '-','_'));
                RETURN id;
            end;
            $$
            """
        ),
        migrations.RunSQL(
            "SELECT id, payment_plan_business_area_for_old_ba(id::text) AS result FROM core_businessarea;"
        ),
        migrations.RunSQL(
            """
            create or replace function payment_business_area_for_old_ba(id text)
               returns text 
               language plpgsql
              as
            $$
            declare 
            -- variable declaration
            begin
                execute format('create sequence if not exists payment_business_area_seq_%s', translate(id::text, '-','_'));
                RETURN id;
            end;
            $$
        """
        ),
        migrations.RunSQL("SELECT id, payment_business_area_for_old_ba(id::text) AS result FROM core_businessarea;"),
    ]
