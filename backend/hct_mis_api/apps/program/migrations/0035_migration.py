# Generated by Django 3.2.13 on 2022-07-11 09:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("program", "0034_migration"), ("targeting", "0007_migration_squashed_0028_migration"),
                    ("steficon", "0003_migration_squashed_0007_empty_rules")]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[],
            database_operations=[migrations.AlterModelTable("CashPlan", "payment_cashplan")],
        )
    ]
