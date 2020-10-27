# Generated by Django 2.2.8 on 2020-05-28 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('definition', models.TextField(blank=True)),
                ('target', models.CharField(max_length=100)),
                ('enabled', models.BooleanField(default=False)),
                ('deprecated', models.BooleanField(default=False)),
                ('language', models.CharField(choices=[('python', 'python'), ('jinja', 'jinja')], max_length=10)),
            ],
        ),
    ]
