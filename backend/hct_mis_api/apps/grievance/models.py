import logging

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.utils import choices_to_dict
from hct_mis_api.apps.payment.models import PaymentVerification
from hct_mis_api.apps.utils.models import ConcurrencyModel, TimeStampedUUIDModel

logger = logging.getLogger(__name__)


class GrievanceTicket(TimeStampedUUIDModel, ConcurrencyModel):
    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "user_modified",
            "created_by",
            "assigned_to",
            "description",
            "admin",
            "area",
            "language",
            "consent",
        ],
        {
            "complaint_ticket_details.payment_record": "payment_record",
            "complaint_ticket_details.household": "household",
            "complaint_ticket_details.individual": "individual",
            "sensitive_ticket_details.payment_record": "payment_record",
            "sensitive_ticket_details.household": "household",
            "sensitive_ticket_details.individual": "individual",
            "household_data_update_ticket_details.household": "household",
            "household_data_update_ticket_details.household_data": "household_data",
            "individual_data_update_ticket_details.individual": "individual",
            "individual_data_update_ticket_details.individual_data": "individual_data",
            "add_individual_ticket_details.household": "household",
            "add_individual_ticket_details.individual_data": "individual_data",
            "delete_individual_ticket_details.individual": "individual",
            "delete_individual_ticket_details.role_reassign_data": "role_reassign_data",
            "system_flagging_ticket_details.golden_records_individual": "golden_records_individual",
            "system_flagging_ticket_details.sanction_list_individual": "sanction_list_individual",
            "needs_adjudication_ticket_details.golden_records_individual": "golden_records_individual",
            "needs_adjudication_ticket_details.possible_duplicate": "possible_duplicate",
            "needs_adjudication_ticket_details.selected_individual": "selected_individual",
            "needs_adjudication_ticket_details.role_reassign_data": "role_reassign_data",
            "payment_verification_ticket_details.payment_verifications": "payment_verifications",
            "payment_verification_ticket_details.payment_verification_status": "payment_verification_status",
            "status_log": "status",
            "category_log": "category",
            "issue_type_log": "issue_type",
        },
    )

    STATUS_NEW = 1
    STATUS_ASSIGNED = 2
    STATUS_IN_PROGRESS = 3
    STATUS_ON_HOLD = 4
    STATUS_FOR_APPROVAL = 5
    STATUS_CLOSED = 6

    CATEGORY_PAYMENT_VERIFICATION = 1
    CATEGORY_DATA_CHANGE = 2
    CATEGORY_SENSITIVE_GRIEVANCE = 3
    CATEGORY_GRIEVANCE_COMPLAINT = 4
    CATEGORY_NEGATIVE_FEEDBACK = 5
    CATEGORY_REFERRAL = 6
    CATEGORY_POSITIVE_FEEDBACK = 7
    CATEGORY_NEEDS_ADJUDICATION = 8
    CATEGORY_SYSTEM_FLAGGING = 9

    ISSUE_TYPE_DATA_BREACH = 1
    ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK = 2
    ISSUE_TYPE_FRAUD_FORGERY = 3
    ISSUE_TYPE_FRAUD_MISUSE = 4
    ISSUE_TYPE_HARASSMENT = 5
    ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT = 6
    ISSUE_TYPE_UNAUTHORIZED_USE = 7
    ISSUE_TYPE_CONFLICT_OF_INTEREST = 8
    ISSUE_TYPE_GROSS_MISMANAGEMENT = 9
    ISSUE_TYPE_PERSONAL_DISPUTES = 10
    ISSUE_TYPE_SEXUAL_HARASSMENT = 11
    ISSUE_TYPE_MISCELLANEOUS = 12

    ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE = 13
    ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE = 14
    ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL = 15
    ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL = 16
    ISSUE_TYPES_CHOICES = {
        CATEGORY_DATA_CHANGE: {
            ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE: _("Household Data Update"),
            ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE: _("Individual Data Update"),
            ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL: _("Add Individual"),
            ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL: _("Withdraw Individual"),
        },
        CATEGORY_SENSITIVE_GRIEVANCE: {
            ISSUE_TYPE_DATA_BREACH: _("Data breach"),
            ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK: _("Bribery, corruption or kickback"),
            ISSUE_TYPE_FRAUD_FORGERY: _("Fraud and forgery"),
            ISSUE_TYPE_FRAUD_MISUSE: _("Fraud involving misuse of programme funds by third party"),
            ISSUE_TYPE_HARASSMENT: _("Harassment and abuse of authority"),
            ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT: _("Inappropriate staff conduct"),
            ISSUE_TYPE_UNAUTHORIZED_USE: _("Unauthorized use, misuse or waste of UNICEF property or funds"),
            ISSUE_TYPE_CONFLICT_OF_INTEREST: _("Conflict of interest"),
            ISSUE_TYPE_GROSS_MISMANAGEMENT: _("Gross mismanagement"),
            ISSUE_TYPE_PERSONAL_DISPUTES: _("Personal disputes"),
            ISSUE_TYPE_SEXUAL_HARASSMENT: _("Sexual harassment and sexual exploitation"),
            ISSUE_TYPE_MISCELLANEOUS: _("Miscellaneous"),
        },
    }
    ALL_ISSUE_TYPES = [choice for choices_group in ISSUE_TYPES_CHOICES.values() for choice in choices_group.items()]
    STATUS_CHOICES = (
        (STATUS_NEW, _("New")),
        (STATUS_ASSIGNED, _("Assigned")),
        (STATUS_IN_PROGRESS, _("In Progress")),
        (STATUS_ON_HOLD, _("On Hold")),
        (STATUS_FOR_APPROVAL, _("For Approval")),
        (STATUS_CLOSED, _("Closed")),
    )

    CATEGORY_CHOICES = (
        (CATEGORY_PAYMENT_VERIFICATION, _("Payment Verification")),
        (CATEGORY_DATA_CHANGE, _("Data Change")),
        (CATEGORY_SENSITIVE_GRIEVANCE, _("Sensitive Grievance")),
        (CATEGORY_GRIEVANCE_COMPLAINT, _("Grievance Complaint")),
        (CATEGORY_NEGATIVE_FEEDBACK, _("Negative Feedback")),
        (CATEGORY_REFERRAL, _("Referral")),
        (CATEGORY_POSITIVE_FEEDBACK, _("Positive Feedback")),
        (CATEGORY_NEEDS_ADJUDICATION, _("Needs Adjudication")),
        (CATEGORY_SYSTEM_FLAGGING, _("System Flagging")),
    )
    MANUAL_CATEGORIES = (
        CATEGORY_DATA_CHANGE,
        CATEGORY_SENSITIVE_GRIEVANCE,
        CATEGORY_GRIEVANCE_COMPLAINT,
        CATEGORY_NEGATIVE_FEEDBACK,
        CATEGORY_REFERRAL,
        CATEGORY_POSITIVE_FEEDBACK,
    )

    SEARCH_TICKET_TYPES_LOOKUPS = {
        "complaint_ticket_details": (
            "individual",
            "household",
            "payment_record",
        ),
        "sensitive_ticket_details": (
            "individual",
            "household",
            "payment_record",
        ),
        "individual_data_update_ticket_details": ("individual", {"household": "individual__household"}),
        "add_individual_ticket_details": ("household",),
        "household_data_update_ticket_details": ("household",),
        "system_flagging_ticket_details": ("golden_records_individual",),
        "needs_adjudication_ticket_details": ("golden_records_individual",),
    }
    FIELD_TICKET_TYPES_LOOKUPS = {
        "complaint_ticket_details": (
            "individual",
            "household",
            "payment_record",
        ),
        "sensitive_ticket_details": (
            "individual",
            "household",
            "payment_record",
        ),
        "individual_data_update_ticket_details": ("individual", "household"),
        "add_individual_ticket_details": ("household",),
        "household_data_update_ticket_details": ("household",),
        "delete_individual_ticket_details": ("individual",),
        "system_flagging_ticket_details": (
            {"individual": "golden_records_individual"},
            {"household": "golden_records_individual.household"},
        ),
        "needs_adjudication_ticket_details": (
            {"individual": "golden_records_individual"},
            {"household": "golden_records_individual.household"},
        ),
    }

    TICKET_DETAILS_NAME_MAPPING = {
        CATEGORY_DATA_CHANGE: {
            ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE: "household_data_update_ticket_details",
            ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE: "individual_data_update_ticket_details",
            ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL: "add_individual_ticket_details",
            ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL: "delete_individual_ticket_details",
        },
        CATEGORY_SENSITIVE_GRIEVANCE: {
            ISSUE_TYPE_DATA_BREACH: "sensitive_ticket_details",
            ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK: "sensitive_ticket_details",
            ISSUE_TYPE_FRAUD_FORGERY: "sensitive_ticket_details",
            ISSUE_TYPE_FRAUD_MISUSE: "sensitive_ticket_details",
            ISSUE_TYPE_HARASSMENT: "sensitive_ticket_details",
            ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT: "sensitive_ticket_details",
            ISSUE_TYPE_UNAUTHORIZED_USE: "sensitive_ticket_details",
            ISSUE_TYPE_CONFLICT_OF_INTEREST: "sensitive_ticket_details",
            ISSUE_TYPE_GROSS_MISMANAGEMENT: "sensitive_ticket_details",
            ISSUE_TYPE_PERSONAL_DISPUTES: "sensitive_ticket_details",
            ISSUE_TYPE_SEXUAL_HARASSMENT: "sensitive_ticket_details",
            ISSUE_TYPE_MISCELLANEOUS: "sensitive_ticket_details",
        },
        CATEGORY_PAYMENT_VERIFICATION: "",
        CATEGORY_GRIEVANCE_COMPLAINT: "complaint_ticket_details",
        CATEGORY_NEGATIVE_FEEDBACK: None,
        CATEGORY_REFERRAL: None,
        CATEGORY_POSITIVE_FEEDBACK: None,
        CATEGORY_NEEDS_ADJUDICATION: "needs_adjudication_ticket_details",
        CATEGORY_SYSTEM_FLAGGING: "system_flagging_ticket_details",
    }

    user_modified = models.DateTimeField(
        verbose_name=_("Modified"),
        null=True,
        blank=True,
        help_text=_("Date this ticket was most recently changed."),
        db_index=True,
    )
    last_notification_sent = models.DateTimeField(
        verbose_name=_("Modified"),
        null=True,
        blank=True,
        help_text=_("Date this ticket was most recently changed."),
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_tickets",
        null=True,
        blank=True,
        verbose_name=_("Created by"),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        null=True,
        blank=True,
        verbose_name=_("Assigned to"),
    )
    status = models.IntegerField(verbose_name=_("Status"), choices=STATUS_CHOICES, default=STATUS_NEW)
    category = models.IntegerField(verbose_name=_("Category"), choices=CATEGORY_CHOICES)
    issue_type = models.IntegerField(verbose_name=_("Type"), null=True, blank=True)
    description = models.TextField(
        verbose_name=_("Description"),
        blank=True,
        help_text=_("The content of the customers query."),
    )
    admin2 = models.ForeignKey("core.AdminArea", null=True, blank=True, on_delete=models.SET_NULL)
    area = models.CharField(max_length=250, blank=True)
    language = models.TextField(blank=True)
    consent = models.BooleanField(default=True)
    business_area = models.ForeignKey("core.BusinessArea", related_name="tickets", on_delete=models.CASCADE)
    linked_tickets = models.ManyToManyField(
        to="GrievanceTicket", through="GrievanceTicketThrough", related_name="linked_tickets_related"
    )
    registration_data_import = models.ForeignKey(
        "registration_data.RegistrationDataImport", null=True, blank=True, on_delete=models.CASCADE
    )
    unicef_id = models.CharField(max_length=250, blank=True, default="")

    @property
    def related_tickets(self):
        combined_related_tickets = (self.linked_tickets.all() | self.linked_tickets_related.all()).distinct()
        yield from combined_related_tickets

    @property
    def is_feedback(self):
        return self.category in (
            self.CATEGORY_NEGATIVE_FEEDBACK,
            self.CATEGORY_POSITIVE_FEEDBACK,
            self.CATEGORY_REFERRAL,
        )

    @property
    def ticket_details(self):
        nested_dict_or_value = self.TICKET_DETAILS_NAME_MAPPING.get(self.category)
        if isinstance(nested_dict_or_value, dict):
            details_name = nested_dict_or_value.get(self.issue_type)
        else:
            details_name = nested_dict_or_value

        return getattr(self, details_name, None)

    @property
    def status_log(self):
        return choices_to_dict(GrievanceTicket.STATUS_CHOICES)[self.status]

    @property
    def category_log(self):
        return choices_to_dict(GrievanceTicket.CATEGORY_CHOICES)[self.category]

    @property
    def issue_type_log(self):
        if self.issue_type is None:
            return None
        issue_type_choices_dict = {}
        for key, value in GrievanceTicket.ISSUE_TYPES_CHOICES.items():
            issue_type_choices_dict.update(value)
        return issue_type_choices_dict[self.issue_type]

    class Meta:
        ordering = (
            "status",
            "created_at",
        )
        verbose_name = "Grievance Ticket"

    def clean(self):
        issue_types = self.ISSUE_TYPES_CHOICES.get(self.category)
        should_contain_issue_types = bool(issue_types)
        has_invalid_issue_type = should_contain_issue_types is True and self.issue_type not in issue_types
        has_issue_type_for_category_without_issue_types = bool(should_contain_issue_types is False and self.issue_type)
        if has_invalid_issue_type or has_issue_type_for_category_without_issue_types:
            logger.error(f"Invalid issue type {self.issue_type} for selected category {self.category}")
            raise ValidationError({"issue_type": "Invalid issue type for selected category"})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.description or str(self.pk)


class GrievanceTicketThrough(TimeStampedUUIDModel):
    main_ticket = models.ForeignKey(
        "GrievanceTicket", on_delete=models.CASCADE, related_name="grievance_tickets_through_main"
    )
    linked_ticket = models.ForeignKey(
        "GrievanceTicket", on_delete=models.CASCADE, related_name="grievance_tickets_through_linked"
    )


class TicketNote(TimeStampedUUIDModel):
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("The content of the customers query."),
    )
    ticket = models.ForeignKey("grievance.GrievanceTicket", related_name="ticket_notes", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="ticket_notes",
        blank=True,
        null=True,
        verbose_name=_("Created by"),
    )


class TicketComplaintDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="complaint_ticket_details", on_delete=models.CASCADE
    )
    payment_record = models.ForeignKey(
        "payment.PaymentRecord",
        related_name="complaint_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    household = models.ForeignKey(
        "household.Household",
        related_name="complaint_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    individual = models.ForeignKey(
        "household.Individual",
        related_name="complaint_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )


class TicketSensitiveDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="sensitive_ticket_details", on_delete=models.CASCADE
    )
    payment_record = models.ForeignKey(
        "payment.PaymentRecord",
        related_name="sensitive_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    household = models.ForeignKey(
        "household.Household",
        related_name="sensitive_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    individual = models.ForeignKey(
        "household.Individual",
        related_name="sensitive_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )


class TicketHouseholdDataUpdateDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="household_data_update_ticket_details", on_delete=models.CASCADE
    )
    household = models.ForeignKey(
        "household.Household",
        related_name="household_data_update_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    household_data = JSONField(null=True)


class TicketIndividualDataUpdateDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="individual_data_update_ticket_details", on_delete=models.CASCADE
    )
    individual = models.ForeignKey(
        "household.Individual",
        related_name="individual_data_update_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    individual_data = JSONField(null=True)

    @property
    def household(self):
        return self.individual.household


class TicketAddIndividualDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="add_individual_ticket_details", on_delete=models.CASCADE
    )
    household = models.ForeignKey(
        "household.Household",
        related_name="add_individual_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    individual_data = JSONField(null=True)
    approve_status = models.BooleanField(default=False)


class TicketDeleteIndividualDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="delete_individual_ticket_details", on_delete=models.CASCADE
    )
    individual = models.ForeignKey(
        "household.Individual",
        related_name="delete_individual_ticket_details",
        on_delete=models.CASCADE,
        null=True,
    )
    role_reassign_data = JSONField(default=dict)
    approve_status = models.BooleanField(default=False)

    @property
    def household(self):
        return self.individual.household


class TicketSystemFlaggingDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="system_flagging_ticket_details", on_delete=models.CASCADE
    )
    golden_records_individual = models.ForeignKey("household.Individual", on_delete=models.CASCADE)
    sanction_list_individual = models.ForeignKey(
        "sanction_list.SanctionListIndividual", related_name="+", on_delete=models.CASCADE
    )
    approve_status = models.BooleanField(default=False)
    role_reassign_data = JSONField(default=dict)


class TicketNeedsAdjudicationDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="needs_adjudication_ticket_details", on_delete=models.CASCADE
    )
    golden_records_individual = models.ForeignKey("household.Individual", related_name="+", on_delete=models.CASCADE)
    possible_duplicate = models.ForeignKey("household.Individual", related_name="+", on_delete=models.CASCADE)
    selected_individual = models.ForeignKey(
        "household.Individual", null=True, related_name="+", on_delete=models.CASCADE
    )
    role_reassign_data = JSONField(default=dict)

    @property
    def has_duplicated_document(self):
        documents1 = [f"{x.document_number}--{x.type_id}" for x in self.golden_records_individual.documents.all()]
        documents2 = [f"{x.document_number}--{x.type_id}" for x in self.possible_duplicate.documents.all()]
        return bool(set(documents1) & set(documents2))


class TicketPaymentVerificationDetails(TimeStampedUUIDModel):
    ticket = models.OneToOneField(
        "grievance.GrievanceTicket", related_name="payment_verification_ticket_details", on_delete=models.CASCADE
    )
    payment_verifications = models.ManyToManyField("payment.PaymentVerification", related_name="ticket_details")
    payment_verification_status = models.CharField(
        max_length=50,
        choices=PaymentVerification.STATUS_CHOICES,
    )
