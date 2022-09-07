# Generated by Django 3.2.13 on 2022-09-07 12:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('household', '0119_migration'),
        ('grievance', '0054_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketcomplaintdetails',
            name='approve_status',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='FeedbackToHousehold',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('message', models.TextField(help_text='The content of the message.', verbose_name='Message')),
                ('kind', models.PositiveSmallIntegerField(choices=[(1, 'Message'), (2, 'Response')])),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feedback_to_household', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('individual', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedback_to_household', to='household.individual')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedback_to_household', to='grievance.grievanceticket')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
