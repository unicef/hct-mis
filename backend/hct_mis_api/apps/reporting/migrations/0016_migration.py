# Generated by Django 3.2.13 on 2022-08-31 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reporting", "0015_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="report",
            name="report_type",
            field=models.IntegerField(
                choices=[
                    (1, "Individuals"),
                    (2, "Households"),
                    (3, "Cash Plan Verification"),
                    (4, "Payments"),
                    (5, "Payment verification"),
                    (10, "Payment Plan"),
                    (6, "Cash Plan"),
                    (7, "Programme"),
                    (8, "Individuals & Payment"),
                    (9, "Grievances"),
                ]
            ),
        ),
    ]
