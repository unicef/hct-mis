# Generated by Django 2.2.16 on 2020-12-10 14:43

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('sanction_list', '0007_migration'),
        ('household', '0039_migration'),
        ('grievance', '0014_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grievanceticket',
            name='category',
            field=models.IntegerField(choices=[(1, 'Payment Verification'), (2, 'Data Change'), (3, 'Sensitive Grievance'), (4, 'Grievance Complaint'), (5, 'Negative Feedback'), (6, 'Referral'), (7, 'Positive Feedback'), (8, 'Needs Adjudication'), (9, 'System Flagging')], verbose_name='Category'),
        ),
        migrations.CreateModel(
            name='TicketSystemFlaggingDetails',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approve_status', models.BooleanField(default=True)),
                ('role_reassign_data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('golden_records_individual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='household.Individual')),
                ('sanction_list_individual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sanction_list.SanctionListIndividual')),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='system_flagging_ticket_details', to='grievance.GrievanceTicket')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TicketNeedsAdjudicationDetails',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('selected_individual', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='household.Individual')),
                ('role_reassign_data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('golden_records_individual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='household.Individual')),
                ('possible_duplicate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='household.Individual')),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='needs_adjudication_ticket_details', to='grievance.GrievanceTicket')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
