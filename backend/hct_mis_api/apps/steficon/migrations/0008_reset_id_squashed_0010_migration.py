# Generated by Django 3.2.19 on 2023-06-10 12:52

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('steficon', '0003_migration_squashed_0007_empty_rules'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RuleCommit',
        ),
        migrations.RemoveField(
            model_name='rule',
            name='id',
        ),
        migrations.AddField(
            model_name='rule',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rule',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rule',
            name='security',
            field=models.IntegerField(choices=[(0, 'Low'), (2, 'Medium'), (4, 'High')], default=2),
        ),
        migrations.AlterField(
            model_name='rule',
            name='definition',
            field=models.TextField(blank=True, default='result.value=0'),
        ),
        migrations.CreateModel(
            name='RuleCommit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('version', models.IntegerField()),
                ('definition', models.TextField(blank=True, default='result.value=0')),
                ('is_release', models.BooleanField(default=False)),
                ('enabled', models.BooleanField(default=False)),
                ('deprecated', models.BooleanField(default=False)),
                ('language', models.CharField(choices=[['python', 'Python'], ['internal', 'internal']], default='python', max_length=10)),
                ('affected_fields', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=None)),
                ('before', django.contrib.postgres.fields.jsonb.JSONField(editable=False, help_text='The record before change')),
                ('after', django.contrib.postgres.fields.jsonb.JSONField(editable=False, help_text='The record after apply changes')),
                ('rule', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='history', to='steficon.rule')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Rule (History)',
                'verbose_name_plural': 'Rules (History)',
                'ordering': ('-timestamp',),
                'get_latest_by': '-timestamp',
            },
        ),
    ]
