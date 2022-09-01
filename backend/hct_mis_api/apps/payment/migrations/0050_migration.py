# Generated by Django 3.2.13 on 2022-07-20 06:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payment", "0049_migration"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cashplanpaymentverification",
            name="status",
            field=models.CharField(
                choices=[
                    ("ACTIVE", "Active"),
                    ("FINISHED", "Finished"),
                    ("PENDING", "Pending"),
                    ("INVALID", "Invalid"),
                ],
                db_index=True,
                default="PENDING",
                max_length=50,
            ),
        )
    ]
