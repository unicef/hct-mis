# Generated by Django 2.2.16 on 2022-01-20 09:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("power_query", "0001_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formatter",
            name="content_type",
            field=models.CharField(
                choices=[
                    ["csv", "text/csv"],
                    ["html", "text/html"],
                    ["json", "application/json"],
                    ["txt", "text/plain"],
                    ["xls", "application/vnd.ms-excel"],
                    ["xml", "application/xml"],
                    ["yaml", "text/yaml"],
                ],
                max_length=5,
            ),
        ),
    ]
