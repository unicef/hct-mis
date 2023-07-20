# Generated by Django 3.2.19 on 2023-06-08 20:01

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
from django.utils import timezone


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
def mark_as_sent(apps, schema_editor):
    try:
        DHHousehold = apps.get_model("mis_datahub", "Household")
        Household = apps.get_model("household", "Household")
        mis_ids = list(DHHousehold.objects.values_list("mis_id", flat=True))
        Household.objects.filter(id__in=mis_ids).update(last_sync_at=timezone.now())
    except:
        pass


def reverse_mark(apps, schema_editor):
    try:
        DHHousehold = apps.get_model("mis_datahub", "Household")
        Household = apps.get_model("household", "Household")
        mis_ids = list(DHHousehold.objects.values_list("mis_id", flat=True))
        Household.objects.filter(id__in=mis_ids).update(last_sync_at=None)
    except:
        pass


def mark_as_sent_program(apps, schema_editor):
    try:
        DHProgram = apps.get_model("mis_datahub", "Program")
        Program = apps.get_model("program", "Program")
        mis_ids = list(DHProgram.objects.values_list("mis_id", flat=True))
        Program.objects.filter(id__in=mis_ids).update(last_sync_at=timezone.now())
    except:
        pass


def reverse_mark_program(apps, schema_editor):
    try:
        DHProgram = apps.get_model("mis_datahub", "Program")
        Program = apps.get_model("program", "Program")
        mis_ids = list(DHProgram.objects.values_list("mis_id", flat=True))
        Program.objects.filter(id__in=mis_ids).update(last_sync_at=None)
    except:
        pass

def unmark_sent_tp(apps, schema_editor):
    try:
        TargetPopulation = apps.get_model("targeting", "TargetPopulation")
        Program = apps.get_model("program", "Program")
        Household = apps.get_model("household", "Household")
        TargetPopulation.objects.filter(
            status="FINALIZED"
        ).update(sent_to_datahub=False)
        Household.objects.update(last_sync_at=None)
        Program.objects.update(last_sync_at=None)
    except:
        pass

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(choices=[('MIS', 'HCT-MIS'), ('CA', 'Cash Assist')], max_length=3)),
                ('status', models.CharField(choices=[('NEW', 'New'), ('READY', 'Ready'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], max_length=11)),
                ('last_modified_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TargetPopulationEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('household_unhcr_id', models.CharField(max_length=255, null=True)),
                ('individual_unhcr_id', models.CharField(max_length=255, null=True)),
                ('household_mis_id', models.UUIDField(null=True)),
                ('individual_mis_id', models.UUIDField(null=True)),
                ('target_population_mis_id', models.UUIDField()),
                ('vulnerability_score', models.DecimalField(blank=True, decimal_places=3, help_text='Written by a tool such as Corticon.', max_digits=6, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TargetPopulation',
            fields=[
                ('mis_id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('population_type', models.CharField(default='HOUSEHOLD', max_length=20)),
                ('targeting_criteria', models.TextField()),
                ('active_households', models.PositiveIntegerField(default=0)),
                ('program_mis_id', models.UUIDField()),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('mis_id', models.UUIDField(primary_key=True, serialize=False)),
                ('business_area', models.CharField(max_length=20)),
                ('ca_id', models.CharField(max_length=255)),
                ('ca_hash_id', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('scope', models.CharField(choices=[('FOR_PARTNERS', 'For partners'), ('UNICEF', 'Unicef')], max_length=50)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('description', models.CharField(max_length=255, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('mis_id', models.UUIDField(primary_key=True, serialize=False)),
                ('unhcr_id', models.CharField(max_length=255, null=True)),
                ('household_mis_id', models.UUIDField()),
                ('status', models.CharField(choices=[('INACTIVE', 'Inactive'), ('ACTIVE', 'Active')], max_length=50, null=True)),
                ('national_id_number', models.CharField(max_length=255, null=True)),
                ('full_name', models.CharField(max_length=255)),
                ('family_name', models.CharField(max_length=255, null=True)),
                ('given_name', models.CharField(max_length=255, null=True)),
                ('middle_name', models.CharField(max_length=255, null=True)),
                ('sex', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], max_length=255)),
                ('date_of_birth', models.DateField()),
                ('estimated_date_of_birth', models.BooleanField()),
                ('relationship', models.CharField(choices=[('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('HEAD', 'Head of household (self)'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('BROTHER_SISTER', 'Brother / Sister'), ('MOTHER_FATHER', 'Mother / Father'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('COUSIN', 'Cousin')], max_length=255, null=True)),
                ('role', models.CharField(choices=[('PRIMARY', 'Primary collector'), ('ALTERNATE', 'Alternate collector'), ('NO_ROLE', 'None')], max_length=255, null=True)),
                ('marital_status', models.CharField(choices=[('SINGLE', 'SINGLE'), ('MARRIED', 'Married'), ('WIDOW', 'Widow'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated')], max_length=255)),
                ('phone_number', models.CharField(max_length=14, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Household',
            fields=[
                ('mis_id', models.UUIDField(primary_key=True, serialize=False)),
                ('unhcr_id', models.CharField(max_length=255, null=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('household_size', models.PositiveIntegerField()),
                ('form_number', models.CharField(max_length=255, null=True)),
                ('address', models.CharField(max_length=255, null=True)),
                ('admin1', models.CharField(max_length=255, null=True)),
                ('admin2', models.CharField(max_length=255, null=True)),
                ('country', django_countries.fields.CountryField(max_length=2, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(mark_as_sent, reverse_mark),
        migrations.RunPython(mark_as_sent_program, reverse_mark_program),
        migrations.RemoveField(
            model_name='individual',
            name='session',
        ),
        migrations.RemoveField(
            model_name='program',
            name='session',
        ),
        migrations.RemoveField(
            model_name='targetpopulation',
            name='session',
        ),
        migrations.RemoveField(
            model_name='targetpopulationentry',
            name='session',
        ),
        migrations.DeleteModel(
            name='Household',
        ),
        migrations.DeleteModel(
            name='Individual',
        ),
        migrations.DeleteModel(
            name='Program',
        ),
        migrations.DeleteModel(
            name='Session',
        ),
        migrations.DeleteModel(
            name='TargetPopulation',
        ),
        migrations.DeleteModel(
            name='TargetPopulationEntry',
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(choices=[('MIS', 'HCT-MIS'), ('CA', 'Cash Assist')], max_length=3)),
                ('status', models.CharField(choices=[('NEW', 'New'), ('READY', 'Ready'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], max_length=11)),
                ('last_modified_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TargetPopulationEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('household_unhcr_id', models.CharField(max_length=255, null=True)),
                ('individual_unhcr_id', models.CharField(max_length=255, null=True)),
                ('household_mis_id', models.UUIDField(null=True)),
                ('individual_mis_id', models.UUIDField(null=True)),
                ('target_population_mis_id', models.UUIDField()),
                ('vulnerability_score', models.DecimalField(blank=True, decimal_places=3, help_text='Written by a tool such as Corticon.', max_digits=6, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
            ],
            options={
                'unique_together': {('session', 'household_mis_id', 'target_population_mis_id')},
            },
        ),
        migrations.CreateModel(
            name='TargetPopulation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_id', models.UUIDField()),
                ('name', models.CharField(max_length=255)),
                ('population_type', models.CharField(default='HOUSEHOLD', max_length=20)),
                ('targeting_criteria', models.TextField()),
                ('active_households', models.PositiveIntegerField(default=0)),
                ('program_mis_id', models.UUIDField()),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
            ],
            options={
                'unique_together': {('session', 'mis_id')},
            },
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_id', models.UUIDField()),
                ('business_area', models.CharField(max_length=20)),
                ('ca_id', models.CharField(max_length=255)),
                ('ca_hash_id', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('scope', models.CharField(choices=[('FOR_PARTNERS', 'For partners'), ('UNICEF', 'Unicef')], max_length=50)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('description', models.CharField(max_length=255, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
            ],
            options={
                'unique_together': {('session', 'mis_id')},
            },
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_id', models.UUIDField()),
                ('unhcr_id', models.CharField(max_length=255, null=True)),
                ('household_mis_id', models.UUIDField()),
                ('status', models.CharField(choices=[('INACTIVE', 'Inactive'), ('ACTIVE', 'Active')], max_length=50, null=True)),
                ('national_id_number', models.CharField(max_length=255, null=True)),
                ('full_name', models.CharField(max_length=255)),
                ('family_name', models.CharField(max_length=255, null=True)),
                ('given_name', models.CharField(max_length=255, null=True)),
                ('middle_name', models.CharField(max_length=255, null=True)),
                ('sex', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], max_length=255)),
                ('date_of_birth', models.DateField()),
                ('estimated_date_of_birth', models.BooleanField()),
                ('relationship', models.CharField(choices=[('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('HEAD', 'Head of household (self)'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('BROTHER_SISTER', 'Brother / Sister'), ('MOTHER_FATHER', 'Mother / Father'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('COUSIN', 'Cousin')], max_length=255, null=True)),
                ('role', models.CharField(choices=[('PRIMARY', 'Primary collector'), ('ALTERNATE', 'Alternate collector'), ('NO_ROLE', 'None')], max_length=255, null=True)),
                ('marital_status', models.CharField(choices=[('SINGLE', 'SINGLE'), ('MARRIED', 'Married'), ('WIDOW', 'Widow'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated')], max_length=255)),
                ('phone_number', models.CharField(max_length=14, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
            ],
            options={
                'unique_together': {('session', 'mis_id')},
            },
        ),
        migrations.CreateModel(
            name='Household',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_id', models.UUIDField()),
                ('unhcr_id', models.CharField(max_length=255, null=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20)),
                ('household_size', models.PositiveIntegerField()),
                ('form_number', models.CharField(max_length=255, null=True)),
                ('address', models.CharField(max_length=255, null=True)),
                ('admin1', models.CharField(max_length=255, null=True)),
                ('admin2', models.CharField(max_length=255, null=True)),
                ('country', django_countries.fields.CountryField(max_length=2, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
            ],
            options={
                'unique_together': {('session', 'mis_id')},
            },
        ),
        migrations.RunPython(unmark_sent_tp, migrations.RunPython.noop),
        migrations.AddField(
            model_name='household',
            name='registration_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='household',
            name='country',
            field=models.CharField(max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='program',
            name='individual_data_needed',
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveField(
            model_name='individual',
            name='role',
        ),
        migrations.AlterField(
            model_name='individual',
            name='household_mis_id',
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name='session',
            name='business_area',
            field=models.CharField(default='0060', help_text='Same as the business area set on program, but\n            this is set as the same value, and all other\n            models this way can get easy access to the business area\n            via the session.', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='individual',
            name='phone_number',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='marital_status',
            field=models.CharField(choices=[('SINGLE', 'SINGLE'), ('MARRIED', 'Married'), ('WIDOWED', 'Widowed'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated')], max_length=255),
        ),
        migrations.AlterField(
            model_name='individual',
            name='marital_status',
            field=models.CharField(choices=[('SINGLE', 'Single'), ('MARRIED', 'Married'), ('WIDOWED', 'Widowed'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated')], max_length=255),
        ),
        migrations.RemoveField(
            model_name='individual',
            name='national_id_number',
        ),
        migrations.AlterField(
            model_name='individual',
            name='relationship',
            field=models.CharField(choices=[('UNKNOWN', 'Unknown'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('HEAD', 'Head of household (self)'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('BROTHER_SISTER', 'Brother / Sister'), ('MOTHER_FATHER', 'Mother / Father'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('COUSIN', 'Cousin')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='household',
            name='residence_status',
            field=models.CharField(choices=[('', 'None'), ('IDP', 'Displaced  |  Internally Displaced People'), ('REFUGEE', 'Displaced  |  Refugee / Asylum Seeker'), ('OTHERS_OF_CONCERN', 'Displaced  |  Others of Concern'), ('HOST', 'Non-displaced  |   Host'), ('NON_HOST', 'Non-displaced  |   Non-host')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='marital_status',
            field=models.CharField(choices=[('', 'None'), ('SINGLE', 'Single'), ('MARRIED', 'Married'), ('WIDOWED', 'Widowed'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated')], max_length=255),
        ),
        migrations.AlterField(
            model_name='individual',
            name='marital_status',
            field=models.CharField(choices=[('', 'None'), ('SINGLE', 'Single'), ('MARRIED', 'Married'), ('WIDOWED', 'Widowed'), ('DIVORCED', 'Divorced'), ('SEPARATED', 'Separated')], max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='pregnant',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='status',
            field=models.CharField(choices=[('NEW', 'New'), ('READY', 'Ready'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('EMPTY', 'Empty')], max_length=11),
        ),
        migrations.AddField(
            model_name='individual',
            name='sanction_list_confirmed_match',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='session',
            name='status',
            field=models.CharField(choices=[('NEW', 'New'), ('READY', 'Ready'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('EMPTY', 'Empty'), ('IGNORED', 'Ignored')], max_length=11),
        ),
        migrations.AddField(
            model_name='session',
            name='sentry_id',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='session',
            name='traceback',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='status',
            field=models.CharField(choices=[('NEW', 'New'), ('READY', 'Ready'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('EMPTY', 'Empty'), ('IGNORED', 'Ignored'), ('LOADING', 'Loading'), ('ERRORED', 'Errored')], max_length=11),
        ),
        migrations.AddField(
            model_name='household',
            name='village',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='program',
            name='ca_hash_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='program',
            name='ca_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='DownPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rec_serial_number', models.CharField(blank=True, max_length=10, null=True)),
                ('business_area', models.CharField(max_length=4)),
                ('down_payment_reference', models.CharField(max_length=20)),
                ('document_type', models.CharField(max_length=10)),
                ('consumed_fc_number', models.CharField(max_length=10)),
                ('total_down_payment_amount_local', models.DecimalField(decimal_places=2, max_digits=15)),
                ('total_down_payment_amount_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('currency_code', models.CharField(blank=True, max_length=5, null=True)),
                ('posting_date', models.DateField(blank=True, null=True)),
                ('doc_year', models.IntegerField(blank=True, null=True)),
                ('doc_number', models.CharField(blank=True, max_length=10, null=True)),
                ('doc_item_number', models.CharField(max_length=3, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('updated_by', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('mis_sync_flag', models.BooleanField(blank=True, default=False, null=True)),
                ('mis_sync_date', models.DateTimeField(blank=True, null=True)),
                ('ca_sync_flag', models.BooleanField(blank=True, default=False, null=True)),
                ('ca_sync_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FundsCommitment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rec_serial_number', models.CharField(blank=True, max_length=10, null=True)),
                ('business_area', models.CharField(blank=True, max_length=4, null=True)),
                ('funds_commitment_number', models.CharField(blank=True, max_length=10, null=True)),
                ('document_type', models.CharField(blank=True, max_length=2, null=True)),
                ('document_text', models.CharField(blank=True, max_length=50, null=True)),
                ('currency_code', models.CharField(blank=True, max_length=5, null=True)),
                ('gl_account', models.CharField(blank=True, max_length=10, null=True)),
                ('commitment_amount_local', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('commitment_amount_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('total_open_amount_local', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('total_open_amount_usd', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('vendor_id', models.CharField(blank=True, max_length=10, null=True)),
                ('posting_date', models.DateField(blank=True, null=True)),
                ('vision_approval', models.CharField(blank=True, max_length=1, null=True)),
                ('document_reference', models.CharField(max_length=16, null=True)),
                ('fc_status', models.CharField(blank=True, max_length=1, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('updated_by', models.CharField(blank=True, default='', max_length=20, null=True)),
                ('mis_sync_flag', models.BooleanField(blank=True, default=False, null=True)),
                ('mis_sync_date', models.DateTimeField(blank=True, null=True)),
                ('ca_sync_flag', models.BooleanField(blank=True, default=False, null=True)),
                ('ca_sync_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='household',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='individual',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='program',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='session',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='targetpopulation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='targetpopulationentry',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='individual',
            name='marital_status',
            field=models.CharField(choices=[('', 'None'), ('DIVORCED', 'Divorced'), ('MARRIED', 'Married'), ('SEPARATED', 'Separated'), ('SINGLE', 'Single'), ('WIDOWED', 'Widowed')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='relationship',
            field=models.CharField(choices=[('UNKNOWN', 'Unknown'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('BROTHER_SISTER', 'Brother / Sister'), ('COUSIN', 'Cousin'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('HEAD', 'Head of household (self)'), ('MOTHER_FATHER', 'Mother / Father'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband')], max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='IndividualRoleInHousehold',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('individual_mis_id', models.UUIDField()),
                ('household_mis_id', models.UUIDField()),
                ('role', models.CharField(blank=True, choices=[('NO_ROLE', 'None'), ('ALTERNATE', 'Alternate collector'), ('PRIMARY', 'Primary collector')], max_length=255)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'unique_together': {('role', 'household_mis_id', 'session')},
            },
        ),
        migrations.AlterField(
            model_name='individual',
            name='relationship',
            field=models.CharField(choices=[('UNKNOWN', 'Unknown'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('BROTHER_SISTER', 'Brother / Sister'), ('COUSIN', 'Cousin'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('HEAD', 'Head of household (self)'), ('MOTHER_FATHER', 'Mother / Father'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('OTHER', 'Other'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband')], max_length=255, null=True),
        ),
        migrations.AlterModelOptions(
            name='targetpopulationentry',
            options={'verbose_name_plural': 'Target Population Entries'},
        ),
        migrations.AddField(
            model_name='household',
            name='unicef_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='individual',
            name='unicef_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='sex',
            field=models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('UNKNOWN', 'Unknown')], max_length=255),
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mis_id', models.UUIDField()),
                ('number', models.CharField(max_length=255, null=True)),
                ('individual_mis_id', models.UUIDField(null=True)),
                ('type', models.CharField(choices=[('BIRTH_CERTIFICATE', 'Birth Certificate'), ('DRIVERS_LICENSE', "Driver's License"), ('ELECTORAL_CARD', 'Electoral Card'), ('NATIONAL_ID', 'National ID'), ('NATIONAL_PASSPORT', 'National Passport'), ('TAX_ID', 'Tax Number Identification'), ('RESIDENCE_PERMIT_NO', "Foreigner's Residence Permit"), ('BANK_STATEMENT', 'Bank Statement'), ('DISABILITY_CERTIFICATE', 'Disability Certificate'), ('FOSTER_CHILD', 'Foster Child'), ('OTHER', 'Other')], max_length=50)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mis_datahub.session')),
                ('date_of_expiry', models.DateField(default=None, null=True)),
                ('photo', models.ImageField(blank=True, default='', upload_to='')),
                ('status', models.CharField(choices=[('VALID', 'Valid'), ('COLLECTED', 'Collected'), ('LOST', 'Lost'), ('UNKNOWN', 'Unknown'), ('CANCELED', 'Canceled'), ('EXPIRED', 'Expired'), ('HOLD', 'Hold'), ('DAMAGED', 'Damaged')], default=None, max_length=30, null=True)),
            ],
            options={
                'unique_together': set(),
            },
        ),
        migrations.AlterField(
            model_name='individual',
            name='relationship',
            field=models.CharField(choices=[('UNKNOWN', 'Unknown'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('BROTHER_SISTER', 'Brother / Sister'), ('COUSIN', 'Cousin'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('HEAD', 'Head of household (self)'), ('MOTHER_FATHER', 'Mother / Father'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('OTHER', 'Other'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('FOSTER_CHILD', 'Foster child')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='individual',
            name='relationship',
            field=models.CharField(choices=[('UNKNOWN', 'Unknown'), ('AUNT_UNCLE', 'Aunt / Uncle'), ('BROTHER_SISTER', 'Brother / Sister'), ('COUSIN', 'Cousin'), ('DAUGHTERINLAW_SONINLAW', 'Daughter-in-law / Son-in-law'), ('GRANDDAUGHER_GRANDSON', 'Granddaughter / Grandson'), ('GRANDMOTHER_GRANDFATHER', 'Grandmother / Grandfather'), ('HEAD', 'Head of household (self)'), ('MOTHER_FATHER', 'Mother / Father'), ('MOTHERINLAW_FATHERINLAW', 'Mother-in-law / Father-in-law'), ('NEPHEW_NIECE', 'Nephew / Niece'), ('NON_BENEFICIARY', 'Not a Family Member. Can only act as a recipient.'), ('OTHER', 'Other'), ('SISTERINLAW_BROTHERINLAW', 'Sister-in-law / Brother-in-law'), ('SON_DAUGHTER', 'Son / Daughter'), ('WIFE_HUSBAND', 'Wife / Husband'), ('FOSTER_CHILD', 'Foster child'), ('FREE_UNION', 'Free union')], max_length=255, null=True),
        ),
    ]
