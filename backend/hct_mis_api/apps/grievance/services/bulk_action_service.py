from typing import List

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.utils import clear_cache_for_key
from hct_mis_api.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hct_mis_api.apps.grievance.models import GrievanceTicket, TicketNote


class BulkActionService:

    def _clear_cache(self, business_area_slug:str):
        cache_key = f"count_{business_area_slug}_GrievanceTicketNodeConnection_"
        clear_cache_for_key(cache_key)
    @transaction.atomic
    def bulk_assign(self, tickets_ids: List[str], assigned_to_id: str, business_area_slug:str) -> QuerySet[GrievanceTicket]:
        user = get_object_or_404(User, id=assigned_to_id)
        queryset = GrievanceTicket.objects.filter(~Q(status=GrievanceTicket.STATUS_CLOSED), id__in=tickets_ids)
        updated_count = queryset.update(assigned_to=user)
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist or are closed")
        self._clear_cache(business_area_slug)
        return queryset

    @transaction.atomic
    def bulk_set_priority(self, tickets_ids: List[str], priority: str, business_area_slug:str) -> QuerySet[GrievanceTicket]:
        if priority not in [x for x, y in PRIORITY_CHOICES]:
            raise ValidationError("Invalid priority")
        queryset = GrievanceTicket.objects.filter(~Q(status=GrievanceTicket.STATUS_CLOSED), id__in=tickets_ids)
        updated_count = queryset.update(priority=priority)
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist or are closed")
        self._clear_cache(business_area_slug)
        return queryset

    @transaction.atomic
    def bulk_set_urgency(self, tickets_ids: List[str], urgency: str, business_area_slug:str) -> QuerySet[GrievanceTicket]:
        if urgency not in [x for x, y in URGENCY_CHOICES]:
            raise ValidationError("Invalid priority")
        queryset = GrievanceTicket.objects.filter(~Q(status=GrievanceTicket.STATUS_CLOSED), id__in=tickets_ids)
        updated_count = queryset.update(urgency=urgency)
        if updated_count != len(tickets_ids):
            raise ValidationError("Some tickets do not exist or are closed")
        self._clear_cache(business_area_slug)
        return queryset

    @transaction.atomic
    def bulk_add_note(self, tickets_ids: List[str], comment: str, business_area_slug:str) -> QuerySet[GrievanceTicket]:
        tickets = GrievanceTicket.objects.filter(~Q(status=GrievanceTicket.STATUS_CLOSED), id__in=tickets_ids)
        if len(tickets) != len(tickets_ids):
            raise ValidationError("Some tickets do not exist, or are closed")
        for ticket in tickets:
            TicketNote.objects.create(ticket=ticket, comment=comment)
        self._clear_cache(business_area_slug)
        return tickets
