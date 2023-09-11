# Generated by Django 3.2.20 on 2023-09-05 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mis_datahub', '0001_migration_squashed_0046_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individual',
            name='relationship',
            field=models.CharField(choices=[('UNKNOWN', 'Unknown'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('BROTHER_SISTER', 'Brother / Sister'), ('COUSIN', 'Cousin'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('HEAD', 'Head of household (self)'), ('MOTHER_FATHER', 'Mother / Father'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('OTHER', 'Other'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('FOSTER_CHILD', 'Foster child'), ('FREE_UNION', 'Free union')], max_length=255, null=True),
        ),
    ]
