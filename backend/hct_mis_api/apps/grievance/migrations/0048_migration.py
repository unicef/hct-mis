# Generated by Django 3.2.13 on 2022-07-29 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0111_migration'),
        ('grievance', '0047_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketneedsadjudicationdetails',
            name='possible_duplicate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='household.individual'),
        ),
    ]
