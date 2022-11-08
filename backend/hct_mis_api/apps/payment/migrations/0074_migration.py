# Generated by Django 3.2.15 on 2022-09-23 18:56

from django.contrib.contenttypes.models import ContentType
from django.db import migrations


def update_payment_verification_fk(apps, schema_editor):
    PaymentVerificationPlan = apps.get_model("payment", "PaymentVerificationPlan")
    PaymentVerificationSummary = apps.get_model("payment", "PaymentVerificationSummary")

    pv_plan_to_upd = []
    pv_summary_to_upd = []

    content_type_for_cash_plan, _ = (
        # need here 'get_or_create' for initdemo if db is empty
        ContentType.objects.get_or_create(app_label="payment", model="cashplan")
    )

    for pv_obj in PaymentVerificationPlan.objects.all():
        if pv_obj.cash_plan:
            pv_obj.payment_plan_content_type_id = content_type_for_cash_plan.id
            pv_obj.payment_plan_object_id = pv_obj.cash_plan_id
            pv_plan_to_upd.append(pv_obj)

    for pv in PaymentVerificationSummary.objects.all():
        if pv.cash_plan:
            pv.payment_plan_content_type_id = content_type_for_cash_plan.id
            pv.payment_plan_object_id = pv.cash_plan_id
            pv_summary_to_upd.append(pv)

    PaymentVerificationPlan.objects.bulk_update(pv_plan_to_upd, ("payment_plan_content_type_id", "payment_plan_object_id"), 1000)
    PaymentVerificationSummary.objects.bulk_update(pv_summary_to_upd, ("payment_plan_content_type_id", "payment_plan_object_id"), 1000)


def update_payment_record_fk(apps, schema_editor):
    PaymentVerification = apps.get_model("payment", "PaymentVerification")
    pv_to_upd = []

    content_type_for_payment_record, _ = (
        # need here 'get_or_create' for initdemo if db is empty
        ContentType.objects.get_or_create(app_label="payment", model="paymentrecord")
    )

    for pv in PaymentVerification.objects.all():
        if pv.payment_record:
            pv.payment_content_type_id = content_type_for_payment_record.id
            pv.payment_object_id = pv.payment_record_id
            pv_to_upd.append(pv)

    PaymentVerification.objects.bulk_update(pv_to_upd, ("payment_content_type_id", "payment_object_id"), 1000)


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0072_migration_squashed_0073_migration'),
    ]

    operations = [
        migrations.RunPython(update_payment_verification_fk,),
        migrations.RunPython(update_payment_record_fk,)
    ]
