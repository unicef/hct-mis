# Generated by Django 3.2.19 on 2023-07-05 07:02
from django.core.paginator import Paginator
from django.db import migrations


def migrate_old_tickets_m2m_program(apps, schema_editor):
    GrievanceTicket = apps.get_model("grievance", "GrievanceTicket")

    qs_tickets = GrievanceTicket.objects.filter(programme__isnull=False)

    paginator = Paginator(qs_tickets, 500)
    for page in paginator.page_range:
        for ticket in paginator.page(page).object_list:
            ticket.programs.add(ticket.programme)


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0038_migration'),
        ('grievance', '0065_migration'),
    ]

    operations = [
        migrations.RunPython(migrate_old_tickets_m2m_program, migrations.RunPython.noop),
    ]
