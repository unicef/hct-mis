# Generated by Django 3.2.18 on 2023-06-29 21:55
import django.db.models.deletion
# Generated by Django 3.2.20 on 2023-08-24 09:53
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0153_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='HouseholdCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unicef_id', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IndividualCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unicef_id', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='household',
            name='household_collection',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='households',
                to='household.HouseholdCollection',
            ),
        ),
        migrations.AddField(
            model_name='individual',
            name='individual_collection',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='individuals',
                to='household.IndividualCollection',
            ),
        ),
        migrations.AlterField(
            model_name='individual',
            name='relationship',
            field=models.CharField(blank=True, choices=[('UNKNOWN', 'Unknown'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('BROTHER_SISTER', 'Brother / Sister'), ('COUSIN', 'Cousin'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('HEAD', 'Head of household (self)'), ('MOTHER_FATHER', 'Mother / Father'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('OTHER', 'Other'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('FOSTER_CHILD', 'Foster child'), ('FREE_UNION', 'Free union')], help_text='This represents the MEMBER relationship. can be blank\n            as well if household is null!', max_length=255),
        ),
    ]
