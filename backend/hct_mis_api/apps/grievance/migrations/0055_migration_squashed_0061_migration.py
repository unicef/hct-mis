# Generated by Django 3.2.19 on 2023-06-28 13:30
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


def do_ticket_complaints_migration(apps, schema_editor):
    from hct_mis_api.apps.payment.models import PaymentRecord

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
                ticket.payment_content_type_id = ContentType.objects.get_for_model(PaymentRecord).id
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


def do_ticket_sensitive_migration(apps, schema_editor):
    from hct_mis_api.apps.payment.models import PaymentRecord

    ticket_sensitive_details = apps.get_model("grievance", "TicketSensitiveDetails")
    start = 1_000
    tickets_to_update = []
    i, count = 0, ticket_sensitive_details.objects.all().count() // start + 1

    while i <= count:
        batch = ticket_sensitive_details.objects.all().order_by("created_at")[start * i: start * (i + 1)]
        for ticket in batch:
            payment_record = getattr(ticket, "payment_record", None)
            if payment_record:
                payment_record_id = payment_record.id
                ticket.payment_object_id = payment_record_id
                ticket.payment_content_type_id = ContentType.objects.get_for_model(PaymentRecord).id
                ticket.payment_record_id = None
                tickets_to_update.append(ticket)

        ticket_sensitive_details.objects.bulk_update(
            tickets_to_update,
            ["payment_record_id", "payment_object_id", "payment_content_type_id"]
        )
        tickets_to_update = []
        i += 1


def undo_ticket_sensitive_migration(apps, schema_editor):
    ticket_sensitive_details = apps.get_model("grievance", "TicketSensitiveDetails")
    start = 1_000
    tickets_to_update = []
    i, count = 0, ticket_sensitive_details.objects.all().count() // start + 1

    while i <= count:
        batch = ticket_sensitive_details.objects.all().order_by("created_at")[start * i: start * (i + 1)]
        for ticket in batch:
            ticket.payment_record_id = ticket.payment_object_id
            ticket.payment_object_id = None
            ticket.payment_content_type_id = None
            tickets_to_update.append(ticket)

        ticket_sensitive_details.objects.bulk_update(
            tickets_to_update,
            ["payment_record_id", "payment_object_id", "payment_content_type_id"]
        )
        tickets_to_update = []
        i += 1


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('grievance', '0054_migration'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0042_migration_squashed_0050_migration'),
        ('program', '0035_migration'),
        ('household', '0147_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketpaymentverificationdetails',
            name='old_received_amount',
            field=models.DecimalField(decimal_places=2, max_digits=12, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))]),
        ),
        migrations.AlterField(
            model_name='grievanceticket',
            name='household_unicef_id',
            field=models.CharField(blank=True, db_index=True, max_length=250, null=True),
        ),
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
        migrations.RunPython(do_ticket_complaints_migration, undo_ticket_complaints_migration,),
        migrations.RemoveField(
            model_name='ticketcomplaintdetails',
            name='payment_record',
        ),
        migrations.AddField(
            model_name='ticketsensitivedetails',
            name='payment_content_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='ticketsensitivedetails',
            name='payment_object_id',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(do_ticket_sensitive_migration, undo_ticket_sensitive_migration),
        migrations.RemoveField(
            model_name='ticketsensitivedetails',
            name='payment_record',
        ),
        migrations.AlterField(
            model_name='ticketneedsadjudicationdetails',
            name='golden_records_individual',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticket_golden_records', to='household.individual'),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.partner'),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='priority',
            field=models.IntegerField(choices=[(0, 'Not set'), (1, 'High'), (2, 'Medium'), (3, 'Low')], default=0, verbose_name='Priority'),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='programme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='program.program'),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='urgency',
            field=models.IntegerField(choices=[(0, 'Not set'), (1, 'Very urgent'), (2, 'Urgent'), (3, 'Not urgent')], default=0, verbose_name='Urgency'),
        ),
        migrations.CreateModel(
            name='GrievanceDocument',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('file_size', models.IntegerField(null=True)),
                ('content_type', models.CharField(max_length=100)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('grievance_ticket', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='support_documents', to='grievance.grievanceticket')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
