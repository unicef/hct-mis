# Generated by Django 3.2.15 on 2023-01-25 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0135_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individual',
            name='preferred_language',
            field=models.CharField(blank=True, choices=[('en-us', 'en-us'), ('ar-ae', 'ar-ae'), ('cs-cz', 'cs-cz'), ('de-de', 'de-de'), ('es-es', 'es-es'), ('fr-fr', 'fr-fr'), ('hu-hu', 'hu-hu'), ('it-it', 'it-it'), ('pl-pl', 'pl-pl'), ('pt-pt', 'pt-pt'), ('ro-ro', 'ro-ro'), ('ru-ru', 'ru-ru'), ('si-si', 'si-si'), ('ta-ta', 'ta-ta'), ('uk-ua', 'uk-ua'), ('hi-hi', 'hi-hi')], max_length=6, null=True),
        ),
    ]
