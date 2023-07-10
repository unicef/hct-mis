# Generated by Django 3.2.13 on 2022-09-23 12:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("geo", "0007_migration"),
        ("core", "0044_migration_squashed_0057_migration"),
        ("program", "0034_migration"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("grievance", "0054_migration"),
        ("household", "0119_migration"),
        ("accountability", "0001_migration"),
    ]

    operations = [
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "id",
                    model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("unicef_id", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "issue_type",
                    models.IntegerField(
                        choices=[(1, "Positive feedback"), (2, "Negative feedback")], verbose_name="Issue type"
                    ),
                ),
                ("description", models.TextField()),
                ("comments", models.TextField(blank=True, null=True)),
                ("area", models.CharField(blank=True, max_length=250)),
                ("language", models.TextField(blank=True)),
                ("consent", models.BooleanField(default=True)),
                (
                    "admin2",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="geo.area"
                    ),
                ),
                (
                    "business_area",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.businessarea"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feedbacks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "household_lookup",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feedbacks",
                        to="household.household",
                        verbose_name="Household lookup",
                    ),
                ),
                (
                    "individual_lookup",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feedbacks",
                        to="household.individual",
                        verbose_name="Individual lookup",
                    ),
                ),
                (
                    "linked_grievance",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="feedback",
                        to="grievance.grievanceticket",
                        verbose_name="Linked grievance",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="program.program"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.RunSQL(
            sql="ALTER TABLE accountability_feedback ADD unicef_id_index SERIAL;",
            reverse_sql="ALTER TABLE accountability_feedback DROP unicef_id_index;",
        ),
        migrations.RunSQL(
            sql="""
        CREATE OR REPLACE FUNCTION create_accountability_communication_feedback_unicef_id() RETURNS trigger
            LANGUAGE plpgsql
            AS $$
        BEGIN
            NEW.unicef_id := format('FED-%s-%s', to_char(NEW.created_at, 'yy'), TRIM(CASE WHEN NEW.unicef_id_index > 9999 THEN NEW.unicef_id_index::varchar(64) ELSE to_char(NEW.unicef_id_index, '0000') END));
            return NEW;
        END
        $$;
        
        CREATE TRIGGER create_accountability_communication_feedback_unicef_id BEFORE INSERT ON accountability_feedback FOR EACH ROW EXECUTE PROCEDURE create_accountability_communication_feedback_unicef_id();
        """,
            reverse_sql="""
            DROP TRIGGER create_accountability_communication_feedback_unicef_id ON accountability_feedback;
            DROP FUNCTION create_accountability_communication_feedback_unicef_id();
            """,
        ),
        migrations.RunSQL(
            sql="UPDATE accountability_feedback SET unicef_id = format('FED-%s-%s', to_char(created_at, 'yy'), TRIM(CASE WHEN unicef_id_index > 9999 THEN unicef_id_index::varchar(64) ELSE to_char(unicef_id_index, '0000') END));",
            reverse_sql="UPDATE accountability_feedback SET unicef_id = NULL;",
        ),
    ]
