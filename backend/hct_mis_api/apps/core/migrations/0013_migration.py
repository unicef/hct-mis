# Generated by Django 2.2.16 on 2021-01-29 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_migration'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adminarealevel',
            options={'ordering': ['name'], 'verbose_name': 'Admin Area Level'},
        ),
        migrations.AddField(
            model_name='adminarealevel',
            name='real_admin_level',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Real Admin Level'),
        ),
        migrations.AlterField(
            model_name='adminarealevel',
            name='business_area',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_area_level', to='core.BusinessArea'),
        ),
    ]
