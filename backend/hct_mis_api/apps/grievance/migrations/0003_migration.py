# Generated by Django 2.2.16 on 2021-04-15 20:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('payment', '0001_migration'),
        ('core', '0001_migration'),
        ('household', '0001_migration'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('grievance', '0002_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketsensitivedetails',
            name='payment_record',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sensitive_ticket_details', to='payment.PaymentRecord'),
        ),
        migrations.AddField(
            model_name='ticketsensitivedetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sensitive_ticket_details', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='ticketpaymentverificationdetails',
            name='payment_verifications',
            field=models.ManyToManyField(related_name='ticket_details', to='payment.PaymentVerification'),
        ),
        migrations.AddField(
            model_name='ticketpaymentverificationdetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment_verification_ticket_details', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='ticketnote',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ticket_notes', to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
        migrations.AddField(
            model_name='ticketnote',
            name='ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ticket_notes', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='ticketneedsadjudicationdetails',
            name='golden_records_individual',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='household.Individual'),
        ),
        migrations.AddField(
            model_name='ticketneedsadjudicationdetails',
            name='possible_duplicate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='household.Individual'),
        ),
        migrations.AddField(
            model_name='ticketneedsadjudicationdetails',
            name='selected_individual',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='household.Individual'),
        ),
        migrations.AddField(
            model_name='ticketneedsadjudicationdetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='needs_adjudication_ticket_details', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='ticketindividualdataupdatedetails',
            name='individual',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='individual_data_update_ticket_details', to='household.Individual'),
        ),
        migrations.AddField(
            model_name='ticketindividualdataupdatedetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='individual_data_update_ticket_details', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='tickethouseholddataupdatedetails',
            name='household',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='household_data_update_ticket_details', to='household.Household'),
        ),
        migrations.AddField(
            model_name='tickethouseholddataupdatedetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='household_data_update_ticket_details', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='ticketdeleteindividualdetails',
            name='individual',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='delete_individual_ticket_details', to='household.Individual'),
        ),
        migrations.AddField(
            model_name='ticketdeleteindividualdetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delete_individual_ticket_details', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='ticketcomplaintdetails',
            name='household',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complaint_ticket_details', to='household.Household'),
        ),
        migrations.AddField(
            model_name='ticketcomplaintdetails',
            name='individual',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complaint_ticket_details', to='household.Individual'),
        ),
        migrations.AddField(
            model_name='ticketcomplaintdetails',
            name='payment_record',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='complaint_ticket_details', to='payment.PaymentRecord'),
        ),
        migrations.AddField(
            model_name='ticketcomplaintdetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='complaint_ticket_details', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='ticketaddindividualdetails',
            name='household',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='add_individual_ticket_details', to='household.Household'),
        ),
        migrations.AddField(
            model_name='ticketaddindividualdetails',
            name='ticket',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='add_individual_ticket_details', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='grievanceticketthrough',
            name='linked_ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grievance_tickets_through_linked', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='grievanceticketthrough',
            name='main_ticket',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grievance_tickets_through_main', to='grievance.GrievanceTicket'),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='admin2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.AdminArea'),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tickets', to=settings.AUTH_USER_MODEL, verbose_name='Assigned to'),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='business_area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='core.BusinessArea'),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tickets', to=settings.AUTH_USER_MODEL, verbose_name='Created by'),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='linked_tickets',
            field=models.ManyToManyField(related_name='linked_tickets_related', through='grievance.GrievanceTicketThrough', to='grievance.GrievanceTicket'),
        ),
    ]
