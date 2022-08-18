# Generated by Django 3.2.13 on 2022-08-17 10:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('payment', '0056_migration'),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION payment_plan_fill_unicef_id_per_business_area_seq() RETURNS trigger
                LANGUAGE plpgsql
                AS $$
                DECLARE businessAreaID varchar;
                DECLARE businessAreaCode varchar;
            begin
                SELECT INTO businessAreaID translate(ba.id::text, '-','_') FROM core_businessarea ba WHERE ba.id=NEW.business_area_id;
                SELECT INTO businessAreaCode ba.code FROM core_businessarea ba WHERE ba.id=NEW.business_area_id;

                NEW.unicef_id := format('PP-%s-%s-%s', trim(businessAreaCode), to_char(NEW.created_at, 'yy'), trim(replace(to_char(nextval('payment_plan_business_area_seq_' || businessAreaID),'00000000'),',','.')));
                RETURN NEW;
            end
            $$;
            """
        ),
        migrations.RunSQL(
            "CREATE TRIGGER payment_plan_fill_unicef_id_per_business_area_seq BEFORE INSERT ON payment_paymentplan FOR EACH ROW EXECUTE PROCEDURE payment_plan_fill_unicef_id_per_business_area_seq();"
        ),

        migrations.RunSQL(
            """
            CREATE OR REPLACE FUNCTION payment_fill_unicef_id_per_business_area_seq() RETURNS trigger
                LANGUAGE plpgsql
                AS $$
                DECLARE businessAreaID varchar;
                DECLARE businessAreaCode varchar;
            begin
                SELECT INTO businessAreaID translate(ba.id::text, '-','_') FROM core_businessarea ba WHERE ba.id=NEW.business_area_id;
                SELECT INTO businessAreaCode ba.code FROM core_businessarea ba WHERE ba.id=NEW.business_area_id;

                NEW.unicef_id := format('RCPT-%s-%s-%s', trim(businessAreaCode), to_char(NEW.created_at, 'yy'), trim(replace(to_char(nextval('payment_business_area_seq_' || businessAreaID),'0,000,000'),',','.')));
                RETURN NEW;
            end
            $$;
            """
        ),
        migrations.RunSQL(
            "CREATE TRIGGER payment_fill_unicef_id_per_business_area_seq BEFORE INSERT ON payment_payment FOR EACH ROW EXECUTE PROCEDURE payment_fill_unicef_id_per_business_area_seq();"
        ),
    ]
