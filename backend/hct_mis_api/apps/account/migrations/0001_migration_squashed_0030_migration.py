# Generated by Django 3.2.19 on 2023-06-08 18:38

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.postgres.fields.citext
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import hct_mis_api.apps.account.fields
import model_utils.fields
import uuid

def update_permissions(apps, schema_editor):
    Role = apps.get_model("account", "Role")
    for role in Role.objects.all():
        if "DASHBOARD_VIEW_HQ" in role.permissions:
            role.permissions.remove("DASHBOARD_VIEW_HQ")
            if "DASHBOARD_VIEW_COUNTRY" not in role.permissions:
                role.permissions.append("DASHBOARD_VIEW_COUNTRY")
            role.save()


def empty_reverse(apps, schema_editor):
    pass


def create_ca_roles(apps, schema_editor):
    Role = apps.get_model('account', 'Role')
    for role in ['Planner/Preparer', 'Approver', 'Authorizer', 'Releaser', 'Card Issuer',
                 'Reconciler', 'Entitlement Formula ', 'Data Exporter', 'Targeting Reader',
                 'Registration Reader Advanced', 'Cash Assistance Reader',]:
        Role.objects.create(name=role, subsystem='CA')


def remove_ca_roles(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Role = apps.get_model('account', 'Role')
    Role.objects.exclude(subsystem='HOPE').delete()


def restore_partner(apps, schema_editor):
    User = apps.get_model("account", "User")  # noqa: F841
    # for user in User.objects.all():
    #     user.org = user.partner.name
    #     user.save()


def set_partner(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    User = apps.get_model("account", "User")
    Partner = apps.get_model("account", "Partner")
    names = (
        "UNICEF",
        "UNHCR",
        "WFP",
    )
    for name in names:
        partner, __ = Partner.objects.get_or_create(name=name, defaults={'is_un': True})
        User.objects.filter(org=name).update(partner=partner)


class Migration(migrations.Migration):

    dependencies = [
        ('steficon', '0002_migration'),
        ('auth', '0011_update_proxy_permissions'),
        ('core', '0002_migration_squashed_0006_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=250, unique=True)),
                ('permissions', hct_mis_api.apps.account.fields.ChoiceArrayField(base_field=models.CharField(choices=[('RDI_VIEW_LIST', 'RDI VIEW LIST'), ('RDI_VIEW_DETAILS', 'RDI VIEW DETAILS'), ('RDI_IMPORT_DATA', 'RDI IMPORT DATA'), ('RDI_RERUN_DEDUPE', 'RDI RERUN DEDUPE'), ('RDI_MERGE_IMPORT', 'RDI MERGE IMPORT'), ('POPULATION_VIEW_HOUSEHOLDS_LIST', 'POPULATION VIEW HOUSEHOLDS LIST'), ('POPULATION_VIEW_HOUSEHOLDS_DETAILS', 'POPULATION VIEW HOUSEHOLDS DETAILS'), ('POPULATION_VIEW_INDIVIDUALS_LIST', 'POPULATION VIEW INDIVIDUALS LIST'), ('POPULATION_VIEW_INDIVIDUALS_DETAILS', 'POPULATION VIEW INDIVIDUALS DETAILS'), ('PRORGRAMME_VIEW_LIST_AND_DETAILS', 'PRORGRAMME VIEW LIST AND DETAILS'), ('PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS', 'PROGRAMME VIEW PAYMENT RECORD DETAILS'), ('PROGRAMME_CREATE', 'PROGRAMME CREATE'), ('PROGRAMME_UPDATE', 'PROGRAMME UPDATE'), ('PROGRAMME_REMOVE', 'PROGRAMME REMOVE'), ('PROGRAMME_ACTIVATE', 'PROGRAMME ACTIVATE'), ('PROGRAMME_FINISH', 'PROGRAMME FINISH'), ('TARGETING_VIEW_LIST', 'TARGETING VIEW LIST'), ('TARGETING_VIEW_DETAILS', 'TARGETING VIEW DETAILS'), ('TARGETING_CREATE', 'TARGETING CREATE'), ('TARGETING_UPDATE', 'TARGETING UPDATE'), ('TARGETING_DUPLICATE', 'TARGETING DUPLICATE'), ('TARGETING_REMOVE', 'TARGETING REMOVE'), ('TARGETING_LOCK', 'TARGETING LOCK'), ('TARGETING_UNLOCK', 'TARGETING UNLOCK'), ('TARGETING_SEND', 'TARGETING SEND'), ('PAYMENT_VERIFICATION_VIEW_LIST', 'PAYMENT VERIFICATION VIEW LIST'), ('PAYMENT_VERIFICATION_VIEW_DETAILS', 'PAYMENT VERIFICATION VIEW DETAILS'), ('PAYMENT_VERIFICATION_CREATE', 'PAYMENT VERIFICATION CREATE'), ('PAYMENT_VERIFICATION_UPDATE', 'PAYMENT VERIFICATION UPDATE'), ('PAYMENT_VERIFICATION_ACTIVATE', 'PAYMENT VERIFICATION ACTIVATE'), ('PAYMENT_VERIFICATION_DISCARD', 'PAYMENT VERIFICATION DISCARD'), ('PAYMENT_VERIFICATION_FINISH', 'PAYMENT VERIFICATION FINISH'), ('PAYMENT_VERIFICATION_EXPORT', 'PAYMENT VERIFICATION EXPORT'), ('PAYMENT_VERIFICATION_IMPORT', 'PAYMENT VERIFICATION IMPORT'), ('PAYMENT_VERIFICATION_VERIFY', 'PAYMENT VERIFICATION VERIFY'), ('PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS', 'PAYMENT VERIFICATION VIEW PAYMENT RECORD DETAILS'), ('USER_MANAGEMENT_VIEW_LIST', 'USER MANAGEMENT VIEW LIST'), ('DASHBOARD_VIEW_COUNTRY', 'DASHBOARD VIEW COUNTRY'), ('DASHBOARD_EXPORT', 'DASHBOARD EXPORT'), ('GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE', 'GRIEVANCES VIEW LIST EXCLUDING SENSITIVE'), ('GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR', 'GRIEVANCES VIEW LIST EXCLUDING SENSITIVE AS CREATOR'), ('GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER', 'GRIEVANCES VIEW LIST EXCLUDING SENSITIVE AS OWNER'), ('GRIEVANCES_VIEW_LIST_SENSITIVE', 'GRIEVANCES VIEW LIST SENSITIVE'), ('GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR', 'GRIEVANCES VIEW LIST SENSITIVE AS CREATOR'), ('GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER', 'GRIEVANCES VIEW LIST SENSITIVE AS OWNER'), ('GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE', 'GRIEVANCES VIEW DETAILS EXCLUDING SENSITIVE'), ('GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR', 'GRIEVANCES VIEW DETAILS EXCLUDING SENSITIVE AS CREATOR'), ('GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER', 'GRIEVANCES VIEW DETAILS EXCLUDING SENSITIVE AS OWNER'), ('GRIEVANCES_VIEW_DETAILS_SENSITIVE', 'GRIEVANCES VIEW DETAILS SENSITIVE'), ('GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR', 'GRIEVANCES VIEW DETAILS SENSITIVE AS CREATOR'), ('GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER', 'GRIEVANCES VIEW DETAILS SENSITIVE AS OWNER'), ('GRIEVANCES_VIEW_HOUSEHOLD_DETAILS', 'GRIEVANCES VIEW HOUSEHOLD DETAILS'), ('GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR', 'GRIEVANCES VIEW HOUSEHOLD DETAILS AS CREATOR'), ('GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER', 'GRIEVANCES VIEW HOUSEHOLD DETAILS AS OWNER'), ('GRIEVANCES_VIEW_INDIVIDUALS_DETAILS', 'GRIEVANCES VIEW INDIVIDUALS DETAILS'), ('GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR', 'GRIEVANCES VIEW INDIVIDUALS DETAILS AS CREATOR'), ('GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER', 'GRIEVANCES VIEW INDIVIDUALS DETAILS AS OWNER'), ('GRIEVANCES_CREATE', 'GRIEVANCES CREATE'), ('GRIEVANCES_UPDATE', 'GRIEVANCES UPDATE'), ('GRIEVANCES_UPDATE_AS_CREATOR', 'GRIEVANCES UPDATE AS CREATOR'), ('GRIEVANCES_UPDATE_AS_OWNER', 'GRIEVANCES UPDATE AS OWNER'), ('GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE', 'GRIEVANCES UPDATE REQUESTED DATA CHANGE'), ('GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR', 'GRIEVANCES UPDATE REQUESTED DATA CHANGE AS CREATOR'), ('GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER', 'GRIEVANCES UPDATE REQUESTED DATA CHANGE AS OWNER'), ('GRIEVANCES_ADD_NOTE', 'GRIEVANCES ADD NOTE'), ('GRIEVANCES_ADD_NOTE_AS_CREATOR', 'GRIEVANCES ADD NOTE AS CREATOR'), ('GRIEVANCES_ADD_NOTE_AS_OWNER', 'GRIEVANCES ADD NOTE AS OWNER'), ('GRIEVANCES_SET_IN_PROGRESS', 'GRIEVANCES SET IN PROGRESS'), ('GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR', 'GRIEVANCES SET IN PROGRESS AS CREATOR'), ('GRIEVANCES_SET_IN_PROGRESS_AS_OWNER', 'GRIEVANCES SET IN PROGRESS AS OWNER'), ('GRIEVANCES_SET_ON_HOLD', 'GRIEVANCES SET ON HOLD'), ('GRIEVANCES_SET_ON_HOLD_AS_CREATOR', 'GRIEVANCES SET ON HOLD AS CREATOR'), ('GRIEVANCES_SET_ON_HOLD_AS_OWNER', 'GRIEVANCES SET ON HOLD AS OWNER'), ('GRIEVANCES_SEND_FOR_APPROVAL', 'GRIEVANCES SEND FOR APPROVAL'), ('GRIEVANCES_SEND_FOR_APPROVAL_AS_CREATOR', 'GRIEVANCES SEND FOR APPROVAL AS CREATOR'), ('GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER', 'GRIEVANCES SEND FOR APPROVAL AS OWNER'), ('GRIEVANCES_SEND_BACK', 'GRIEVANCES SEND BACK'), ('GRIEVANCES_SEND_BACK_AS_CREATOR', 'GRIEVANCES SEND BACK AS CREATOR'), ('GRIEVANCES_SEND_BACK_AS_OWNER', 'GRIEVANCES SEND BACK AS OWNER'), ('GRIEVANCES_APPROVE_DATA_CHANGE', 'GRIEVANCES APPROVE DATA CHANGE'), ('GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR', 'GRIEVANCES APPROVE DATA CHANGE AS CREATOR'), ('GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER', 'GRIEVANCES APPROVE DATA CHANGE AS OWNER'), ('GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK', 'GRIEVANCES CLOSE TICKET EXCLUDING FEEDBACK'), ('GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR', 'GRIEVANCES CLOSE TICKET EXCLUDING FEEDBACK AS CREATOR'), ('GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER', 'GRIEVANCES CLOSE TICKET EXCLUDING FEEDBACK AS OWNER'), ('GRIEVANCES_CLOSE_TICKET_FEEDBACK', 'GRIEVANCES CLOSE TICKET FEEDBACK'), ('GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR', 'GRIEVANCES CLOSE TICKET FEEDBACK AS CREATOR'), ('GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER', 'GRIEVANCES CLOSE TICKET FEEDBACK AS OWNER'), ('GRIEVANCES_APPROVE_FLAG_AND_DEDUPE', 'GRIEVANCES APPROVE FLAG AND DEDUPE'), ('GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR', 'GRIEVANCES APPROVE FLAG AND DEDUPE AS CREATOR'), ('GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER', 'GRIEVANCES APPROVE FLAG AND DEDUPE AS OWNER'), ('REPORTING_EXPORT', 'REPORTING EXPORT'), ('ALL_VIEW_PII_DATA_ON_LISTS', 'ALL VIEW PII DATA ON LISTS'), ('ACTIVITY_LOG_VIEW', 'ACTIVITY LOG VIEW'), ('ACTIVITY_LOG_DOWNLOAD', 'ACTIVITY LOG DOWNLOAD')], max_length=255), blank=True, null=True, size=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
                ('partner', models.CharField(choices=[('UNHCR', 'UNHCR'), ('WFP', 'WFP'), ('UNICEF', 'UNICEF')], default='UNICEF', max_length=10)),
                ('status', models.CharField(choices=[('INVITED', 'Invited'), ('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='INVITED', max_length=10)),
                ('available_for_export', models.BooleanField(default=True, help_text='Indicating if a User can be exported to CashAssist')),
                ('job_title', models.CharField(blank='', default='', max_length=255)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_roles', to='core.businessarea')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_roles', to='account.role')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_roles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'unique_together': {('business_area', 'user', 'role')},
            },
        ),
        migrations.CreateModel(
            name='incompatibleroles',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('role_one', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incompatible_roles_one', to='account.role')),
                ('role_two', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incompatible_roles_two', to='account.role')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'incompatible roles',
                'verbose_name_plural': 'incompatible roles',
                'unique_together': {('role_one', 'role_two')},
            },
        ),
        migrations.RunPython(update_permissions, empty_reverse),
        migrations.AlterField(
            model_name='incompatibleroles',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='incompatibleroles',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='userrole',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='userrole',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(max_length=250, unique=True, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255), django.core.validators.RegexValidator('\\s{2,}', 'Double spaces characters are not allowed.', code='double_spaces_characters_not_allowed', inverse_match=True), django.core.validators.RegexValidator('(^\\s+)|(\\s+$)', 'Leading or trailing spaces characters are not allowed.', code='leading_trailing_spaces_characters_not_allowed', inverse_match=True), django.core.validators.ProhibitNullCharactersValidator()]),
        ),
        migrations.AddField(
            model_name='user',
            name='ad_uuid',
            field=models.CharField(blank=True, editable=False, max_length=64, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='job_title',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='custom_fields',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('can_load_from_ad', 'Can load users from ActiveDirectory'), ('can_sync_with_ad', 'Can synchronise user with ActiveDirectory'), ('can_upload_to_kobo', 'Can upload users to Kobo'), ('can_import_from_kobo', 'Can import and sync users from Kobo'), ('can_debug', 'Can access debug informations'), ('can_inspect', 'Can inspect objects'))},
        ),
        migrations.AddField(
            model_name='user',
            name='last_doap_sync',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_modify_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='role',
            name='subsystem',
            field=models.CharField(choices=[('HOPE', 'HOPE'), ('KOBO', 'Kobo'), ('CA', 'CashAssist')], default='HOPE', max_length=30),
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(max_length=250, validators=[django.core.validators.MinLengthValidator(3), django.core.validators.MaxLengthValidator(255), django.core.validators.RegexValidator('\\s{2,}', 'Double spaces characters are not allowed.', code='double_spaces_characters_not_allowed', inverse_match=True), django.core.validators.RegexValidator('(^\\s+)|(\\s+$)', 'Leading or trailing spaces characters are not allowed.', code='leading_trailing_spaces_characters_not_allowed', inverse_match=True), django.core.validators.ProhibitNullCharactersValidator()]),
        ),
        migrations.AlterUniqueTogether(
            name='role',
            unique_together={('name', 'subsystem')},
        ),
        migrations.RunPython(create_ca_roles, remove_ca_roles),
        migrations.RenameField(
            model_name='user',
            old_name='partner',
            new_name='org',
        ),
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', django.contrib.postgres.fields.citext.CICharField(max_length=100, unique=True)),
                ('is_un', models.BooleanField(default=False, verbose_name='U.N.')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='account.partner'),
        ),
        migrations.RunPython(set_partner, restore_partner),
        migrations.RemoveField(
            model_name='user',
            name='org',
        ),
        migrations.AddField(
            model_name='user',
            name='doap_hash',
            field=models.TextField(default='', editable=False),
        ),
    ]
