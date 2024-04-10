# Generated by Django 3.2.25 on 2024-04-07 21:43

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0066_migration'),
        ('geo', '0008_migration'),
        ('program', '0046_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramPartnerThrough',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('areas', models.ManyToManyField(blank=True, related_name='program_partner_through', to='geo.Area')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_partner_through', to='account.partner')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_partner_through', to='program.program')),
            ],
        ),
        migrations.AddField(
            model_name='program',
            name='partners',
            field=models.ManyToManyField(related_name='programs', through='program.ProgramPartnerThrough', to='account.Partner'),
        ),
        migrations.AddConstraint(
            model_name='programpartnerthrough',
            constraint=models.UniqueConstraint(fields=('program', 'partner'), name='unique_program_partner'),
        ),
    ]
