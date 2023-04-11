# Generated by Django 3.2.18 on 2023-04-05 14:46

from django.db import migrations, models
import django.db.models.deletion


def do_ticket_complaints_migration(apps, schema_editor):
    ticket_complaint_details = apps.get_model("grievance", "TicketComplaintDetails")
    start = 1_000
    tickets_to_update = []
    i, count = 0, ticket_complaint_details.objects.all().count() // start + 1

    while i <= count:
        batch = ticket_complaint_details.objects.all().order_by("created_at")[start * i: start * (i + 1)]
        for ticket in batch:
            payment_record = getattr(ticket, "payment_record", None)
            if payment_record:
                payment_record_id = payment_record.id
                ticket.payment_object_id = payment_record_id
                ticket.payment_content_type_id = 80  # Only PaymentRecords
                ticket.payment_record_id = None
                tickets_to_update.append(ticket)

        ticket_complaint_details.objects.bulk_update(
            tickets_to_update,
            ["payment_record_id", "payment_object_id", "payment_content_type_id"]
        )
        tickets_to_update = []
        i += 1


def undo_ticket_complaints_migration(apps, schema_editor):
    ticket_complaint_details = apps.get_model("grievance", "TicketComplaintDetails")
    start = 1_000
    tickets_to_update = []
    i, count = 0, ticket_complaint_details.objects.all().count() // start + 1

    while i <= count:
        batch = ticket_complaint_details.objects.all().order_by("created_at")[start * i: start * (i + 1)]
        for ticket in batch:
            ticket.payment_record_id = ticket.payment_object_id
            ticket.payment_object_id = None
            ticket.payment_content_type_id = None
            tickets_to_update.append(ticket)

        ticket_complaint_details.objects.bulk_update(
            tickets_to_update,
            ["payment_record_id", "payment_object_id", "payment_content_type_id"]
        )
        tickets_to_update = []
        i += 1


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('grievance', '0056_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketcomplaintdetails',
            name='payment_content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='ticketcomplaintdetails',
            name='payment_object_id',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(do_ticket_complaints_migration, undo_ticket_complaints_migration),
        migrations.RemoveField(
            model_name='ticketcomplaintdetails',
            name='payment_record',
        ),
    ]
