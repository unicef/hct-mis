# Generated by Django 3.2.22 on 2023-11-09 08:15

from django.db import migrations, models
import django.db.models.deletion


def add_default_partner(apps, schema_editor):
    User = apps.get_model("account", "User")
    Partner = apps.get_model("account", "Partner")

    default_partner, _ = Partner.objects.get_or_create(name="UNICEF")
    User.objects.filter(partner__isnull=True).update(partner=default_partner)


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0055_migration'),
    ]

    operations = [
        migrations.RunPython(add_default_partner, migrations.RunPython.noop),
        migrations.AddField(
            model_name='partner',
            name='permissions',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='user',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='account.partner'),
        ),
    ]
