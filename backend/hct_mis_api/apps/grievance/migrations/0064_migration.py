# Generated by Django 3.2.20 on 2023-10-03 12:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0063_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticketaddindividualdetails',
            options={'verbose_name_plural': 'Ticket Add Individual Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketcomplaintdetails',
            options={'verbose_name_plural': 'Ticket Complaint Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketdeletehouseholddetails',
            options={'verbose_name_plural': 'Ticket Delete Household Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketdeleteindividualdetails',
            options={'verbose_name_plural': 'Ticket Delete Individual Details'},
        ),
        migrations.AlterModelOptions(
            name='tickethouseholddataupdatedetails',
            options={'verbose_name_plural': 'Ticket Household Data Update Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketindividualdataupdatedetails',
            options={'verbose_name_plural': 'Ticket Individual Data Update Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketneedsadjudicationdetails',
            options={'verbose_name_plural': 'Ticket Needs Adjudication Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketnegativefeedbackdetails',
            options={'verbose_name_plural': 'Ticket Negative Feedback Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketpaymentverificationdetails',
            options={'verbose_name_plural': 'Ticket Payment Verification Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketpositivefeedbackdetails',
            options={'verbose_name_plural': 'Ticket Positive Feedback Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketreferraldetails',
            options={'verbose_name_plural': 'Ticket Referral Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketsensitivedetails',
            options={'verbose_name_plural': 'Ticket Sensitive Details'},
        ),
        migrations.AlterModelOptions(
            name='ticketsystemflaggingdetails',
            options={'verbose_name_plural': 'Ticket System Flagging Details'},
        ),
    ]
