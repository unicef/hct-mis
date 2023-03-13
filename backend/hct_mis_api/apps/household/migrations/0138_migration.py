# Generated by Django 3.2.15 on 2023-03-13 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('household', '0137_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='cleared',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='individual',
            name='relationship_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='type',
            field=models.CharField(choices=[('BIRTH_CERTIFICATE', 'Birth Certificate'), ('DRIVERS_LICENSE', "Driver's License"), ('ELECTORAL_CARD', 'Electoral Card'), ('NATIONAL_ID', 'National ID'), ('NATIONAL_PASSPORT', 'National Passport'), ('TAX_ID', 'Tax Number Identification'), ('RESIDENCE_PERMIT_NO', "Foreigner's Residence Permit"), ('BANK_STATEMENT', 'Bank Statement'), ('FOSTER_CHILD', 'Foster Child'), ('OTHER', 'Other')], max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='relationship',
            field=models.CharField(blank=True, choices=[('UNKNOWN', 'Unknown'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('BROTHER_SISTER', 'Brother / Sister'), ('COUSIN', 'Cousin'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('HEAD', 'Head of household (self)'), ('MOTHER_FATHER', 'Mother / Father'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('OTHER', 'Other'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('FOSTER_CHILD', 'Foster child')], help_text='This represents the MEMBER relationship. can be blank\n            as well if household is null!', max_length=255),
        ),
    ]
