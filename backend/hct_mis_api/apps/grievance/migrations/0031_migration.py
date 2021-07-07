# Generated by Django 2.2.16 on 2021-07-07 10:19

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0077_migration'),
        ('grievance', '0030_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketPositiveFeedbackDetails',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('household', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='positive_feedback_ticket_details', to='household.Household')),
                ('individual', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='positive_feedback_ticket_details', to='household.Individual')),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='positive_feedback_ticket_details', to='grievance.GrievanceTicket')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TicketNegativeFeedbackDetails',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('household', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='negative_feedback_ticket_details', to='household.Household')),
                ('individual', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='negative_feedback_ticket_details', to='household.Individual')),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='negative_feedback_ticket_details', to='grievance.GrievanceTicket')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
