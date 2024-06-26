# Generated by Django 3.2.15 on 2022-10-27 07:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0075_migration'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentverificationplan',
            name='cash_plan',
        ),
        migrations.RemoveField(
            model_name='paymentverificationsummary',
            name='cash_plan',
        ),
        migrations.RemoveField(
            model_name='paymentverification',
            name='payment_record',
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[('Distribution Successful', 'Distribution Successful'), ('Not Distributed', 'Not Distributed'), ('Transaction Successful', 'Transaction Successful'), ('Transaction Erroneous', 'Transaction Erroneous'), ('Force failed', 'Force failed')], max_length=255),
        ),
        migrations.AlterField(
            model_name='paymentverification',
            name='payment_content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='paymentverification',
            name='payment_object_id',
            field=models.UUIDField(),
        ),
        migrations.AlterField(
            model_name='paymentverificationplan',
            name='payment_plan_content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='paymentverificationplan',
            name='payment_plan_object_id',
            field=models.UUIDField(),
        ),
        migrations.AlterField(
            model_name='paymentverificationplan',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('FINISHED', 'Finished'), ('PENDING', 'Pending'), ('INVALID', 'Invalid'), ('RAPID_PRO_ERROR', 'RapidPro Error')], db_index=True, default='PENDING', max_length=50),
        ),
        migrations.AlterField(
            model_name='paymentverificationsummary',
            name='payment_plan_content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='paymentverificationsummary',
            name='payment_plan_object_id',
            field=models.UUIDField(),
        ),
        migrations.AddIndex(
            model_name='paymentverification',
            index=models.Index(fields=['payment_content_type', 'payment_object_id'], name='payment_pay_payment_ec4a29_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentverificationplan',
            index=models.Index(fields=['payment_plan_content_type', 'payment_plan_object_id'], name='payment_pay_payment_3ba67e_idx'),
        ),
        migrations.AddIndex(
            model_name='paymentverificationsummary',
            index=models.Index(fields=['payment_plan_content_type', 'payment_plan_object_id'], name='payment_pay_payment_8b7d61_idx'),
        ),
    ]
