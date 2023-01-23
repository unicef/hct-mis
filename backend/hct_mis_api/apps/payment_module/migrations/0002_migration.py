# Generated by Django 3.2.15 on 2023-01-20 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment_module', '0001_migration'),
    ]

    operations = [
        migrations.RenameField(
            model_name='paymentplan',
            old_name='steficon_applied_date',
            new_name='rule_engine_applied_date',
        ),
        migrations.RenameField(
            model_name='paymentplan',
            old_name='steficon_rule_commit',
            new_name='rule_engine_rule_commit',
        ),
        migrations.RemoveField(
            model_name='paymentplan',
            name='targeting_criteria',
        ),
        migrations.AddField(
            model_name='paymentcycle',
            name='title',
            field=models.CharField(default='missing-title', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentplan',
            name='payment_cycle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_plans', to='payment_module.paymentcycle'),
        ),
    ]
