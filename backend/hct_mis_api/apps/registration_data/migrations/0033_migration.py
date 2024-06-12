# Generated by Django 3.2.23 on 2024-01-11 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration_data', '0032_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrationdataimport',
            name='data_source',
            field=models.CharField(choices=[('XLS', 'Excel'), ('KOBO', 'KoBo'), ('FLEX_REGISTRATION', 'Flex Registration'), ('API', 'Flex API'), ('EDOPOMOGA', 'eDopomoga'), ('PROGRAM_POPULATION', 'Program Population')], max_length=255),
        ),
    ]