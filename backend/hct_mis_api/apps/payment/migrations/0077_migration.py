# Generated by Django 3.2.15 on 2022-11-08 14:40

from django.db import migrations


def update_xlsx_payment_verification_plan_file(apps, schema_editor):
    XlsxPaymentVerificationPlanFile = apps.get_model("payment", "XlsxPaymentVerificationPlanFile")
    FileTemp = apps.get_model("core", "FileTemp")
    PaymentVerificationPlan = apps.get_model("payment", "PaymentVerificationPlan")
    ContentType = apps.get_model("contenttypes", "ContentType")

    ct = ContentType.objects.get_for_model(PaymentVerificationPlan)
    objs_create_list = []

    for xlsx in XlsxPaymentVerificationPlanFile.objects.all():
        new_obj = FileTemp(
            file=xlsx.file,
            object_id=xlsx.payment_verification_plan.pk,
            content_type_id=ct.pk,
            was_downloaded=xlsx.was_downloaded,
            created_by=xlsx.created_by,
            created_at=xlsx.created_at,
        )
        objs_create_list.append(new_obj)

    FileTemp.objects.bulk_create(objs_create_list, 1000)


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("payment", "0075_migration_squashed_0076_migration"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="deliverymechanismperpaymentplan",
            unique_together=set(),
        ),
        migrations.RunPython(update_xlsx_payment_verification_plan_file, backward),

    ]
