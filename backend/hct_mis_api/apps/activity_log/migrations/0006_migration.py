# Generated by Django 3.2.19 on 2023-07-12 07:38

from django.db import migrations, models
import django.db.models.deletion

from django.core.paginator import Paginator
from django.db import migrations, models


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
        ('activity_log', '0005_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='logentry',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='program.program'),
        ),
    ]
