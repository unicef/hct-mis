# Generated by Django 3.2.15 on 2022-09-21 13:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0053_migration'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='APIToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, max_length=40, unique=True, verbose_name='Key')),
                ('allowed_ips', models.CharField(blank=True, max_length=200, null=True, verbose_name='IPs')),
                ('valid_from', models.DateField(default=django.utils.timezone.now)),
                ('valid_to', models.DateField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('valid_for', models.ManyToManyField(blank=True, to='core.BusinessArea')),
            ],
        ),
    ]
