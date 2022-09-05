# Generated by Django 3.2.13 on 2022-08-22 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0060_migration"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="deliverymechanismperpaymentplan",
            name="unique payment_plan_delivery_mechanism",
        ),
        migrations.RemoveConstraint(
            model_name="deliverymechanismperpaymentplan",
            name="unique payment_plan_delivery_mechanism_order",
        ),
        migrations.AddConstraint(
            model_name="deliverymechanismperpaymentplan",
            constraint=models.UniqueConstraint(
                fields=("payment_plan", "delivery_mechanism", "delivery_mechanism_order"),
                name="unique payment_plan_delivery_mechanism",
            ),
        ),
    ]
