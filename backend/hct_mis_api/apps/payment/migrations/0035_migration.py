# Generated by Django 2.2.26 on 2022-02-17 12:01

from django.db import migrations


def empty_reverse(apps, schema_editor):
    pass


def move_status_to_summary(apps, schema_editor):
    CashPlan = apps.get_model("program", "CashPlan")
    CashPlanPaymentVerificationSummary = apps.get_model("payment", "CashPlanPaymentVerificationSummary")
    for cash_plan in CashPlan.objects.all():
        verification = cash_plan.verifications.first()
        activation_date = None
        completion_date = None
        if verification:
            activation_date = verification.activation_date
            completion_date = verification.completion_date
        CashPlanPaymentVerificationSummary.objects.create(
            status=cash_plan.verification_status,
            cash_plan=cash_plan,
            activation_date=activation_date,
            completion_date=completion_date,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0034_migration"),
    ]

    operations = [
        migrations.RunPython(move_status_to_summary, empty_reverse),
    ]
