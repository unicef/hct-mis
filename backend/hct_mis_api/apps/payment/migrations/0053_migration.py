# Generated by Django 3.2.13 on 2022-08-03 09:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0052_migration"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="approval",
            options={"ordering": ("-created_at",)},
        ),
        migrations.AlterModelOptions(
            name="approvalprocess",
            options={"ordering": ("-created_at",), "verbose_name_plural": "Approval Processes"},
        ),
    ]
