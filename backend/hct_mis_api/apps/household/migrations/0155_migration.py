# Generated by Django 3.2.19 on 2023-07-10 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0154_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='household',
            name='copied_from',
            field=models.ForeignKey(blank=True, help_text='If this household was copied from another household, this field will contain the household it was copied from.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='copied_to', to='household.household'),
        ),
        migrations.AddField(
            model_name='individual',
            name='copied_from',
            field=models.ForeignKey(blank=True, help_text='If this individual was copied from another individual, this field will contain the individual it was copied from.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='copied_to', to='household.individual'),
        ),
    ]
