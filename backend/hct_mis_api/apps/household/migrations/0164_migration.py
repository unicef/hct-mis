# Generated by Django 3.2.22 on 2023-12-20 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0163_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='household',
            name='residence_status',
            field=models.CharField(choices=[('', 'None'), ('IDP', 'Displaced  |  Internally Displaced People'), ('REFUGEE', 'Displaced  |  Refugee / Asylum Seeker'), ('OTHERS_OF_CONCERN', 'Displaced  |  Others of Concern'), ('HOST', 'Non-displaced  |   Host'), ('NON_HOST', 'Non-displaced  |   Non-host'), ('RETURNEE', 'Displaced  |   Returnee')], max_length=254),
        ),
    ]
