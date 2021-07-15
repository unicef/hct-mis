# Generated by Django 2.2.16 on 2021-07-13 08:15

from django.db import migrations
from django.db.models import F


def restore_partner(apps, schema_editor):
    User = apps.get_model('account', 'User')
    # for user in User.objects.all():
    #     user.org = user.partner.name
    #     user.save()


def set_partner(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    User = apps.get_model('account', 'User')
    Partner = apps.get_model('account', 'Partner')
    names = ("UNICEF", "UNHCR", "WFP",)
    for name in names:
        partner, __ = Partner.objects.get_or_create(name=name, is_un=True)
        User.objects.filter(org=name).update(partner=partner)


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0028_migration'),
    ]

    operations = [
        migrations.RunPython(set_partner, restore_partner),

    ]
