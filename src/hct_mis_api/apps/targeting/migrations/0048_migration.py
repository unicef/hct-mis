# Generated by Django 3.2.25 on 2024-10-09 13:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0053_migration'),
        ('targeting', '0047_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='targetpopulation',
            name='program',
            field=models.ForeignKey(help_text='Set only when the target population moves from draft to\n            candidate list frozen state (approved)', on_delete=django.db.models.deletion.PROTECT, to='program.program'),
        ),
    ]
