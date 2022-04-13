# Generated by Django 3.2.12 on 2022-04-13 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0100_migration'),
        ('grievance', '0037_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketneedsadjudicationdetails',
            name='is_multiple_duplicates_version',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ticketneedsadjudicationdetails',
            name='possible_duplicates',
            field=models.ManyToManyField(related_name='ticket_duplicates', to='household.Individual'),
        ),
    ]
