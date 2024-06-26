# Generated by Django 3.2.20 on 2023-09-18 11:23

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0069_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataCollectingType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('code', models.CharField(max_length=60, unique=True)),
                ('description', models.TextField(blank=True)),
                ('compatible_types', models.ManyToManyField(blank=True, related_name='_core_datacollectingtype_compatible_types_+', to='core.DataCollectingType')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
