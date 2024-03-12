# Generated by Django 3.2.24 on 2024-02-16 05:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('grievance', '0050_migration'), ('grievance', '0051_migration'), ('grievance', '0052_migration'), ('grievance', '0053_migration'), ('grievance', '0054_migration')]

    dependencies = [
        ('household', '0126_migration'),
        ('grievance', '0035_migration_squashed_0049_migration'),
        ('household', '0119_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketneedsadjudicationdetails',
            name='possible_duplicate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='household.individual'),
        ),
        migrations.AlterField(
            model_name='grievanceticket',
            name='unicef_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='grievanceticket',
            name='linked_tickets',
            field=models.ManyToManyField(related_name='_grievance_grievanceticket_linked_tickets_+', through='grievance.GrievanceTicketThrough', to='grievance.GrievanceTicket'),
        ),
        migrations.AddConstraint(
            model_name='grievanceticketthrough',
            constraint=models.UniqueConstraint(fields=('main_ticket', 'linked_ticket'), name='unique_main_linked_ticket'),
        ),
        migrations.AddField(
            model_name='ticketdeletehouseholddetails',
            name='reason_household',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='household.household'),
        ),
        migrations.AlterField(
            model_name='grievanceticket',
            name='category',
            field=models.IntegerField(choices=[(8, 'Needs Adjudication'), (1, 'Payment Verification'), (9, 'System Flagging'), (2, 'Data Change'), (4, 'Grievance Complaint'), (5, 'Negative Feedback'), (7, 'Positive Feedback'), (6, 'Referral'), (3, 'Sensitive Grievance')], verbose_name='Category'),
        ),
    ]