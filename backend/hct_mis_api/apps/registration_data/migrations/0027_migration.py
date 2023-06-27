# Generated by Django 3.2.19 on 2023-06-27 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0038_migration'),
        ('registration_data', '0026_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationdataimport',
            name='program',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registration_imports', to='program.program'),
        ),
    ]
