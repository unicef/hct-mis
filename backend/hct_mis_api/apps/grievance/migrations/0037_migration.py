# Generated by Django 3.2.12 on 2022-03-17 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grievance', '0036_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grievanceticket',
            name='category',
            field=models.IntegerField(choices=[(2, 'Data Change'), (4, 'Grievance Complaint'), (8, 'Needs Adjudication'), (5, 'Negative Feedback'), (1, 'Payment Verification'), (7, 'Positive Feedback'), (6, 'Referral'), (3, 'Sensitive Grievance'), (9, 'System Flagging')], verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='grievanceticket',
            name='status',
            field=models.IntegerField(choices=[(1, 'New'), (2, 'Assigned'), (6, 'Closed'), (5, 'For Approval'), (3, 'In Progress'), (4, 'On Hold')], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='ticketdeletehouseholddetails',
            name='role_reassign_data',
            field=models.JSONField(default=dict),
        ),
    ]
