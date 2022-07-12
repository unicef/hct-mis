import graphene
from django.db.models import Case, CharField, Count, When, Value, Q, Avg, F
from django.utils.encoding import force_str

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.utils.schema import ChartDatasetNode


def transform_to_chart_dataset(qs):
    labels, data = [], []
    for q in qs:
        label, value = q
        labels.append(label)
        data.append(value)

    return {
        "labels": labels,
        "datasets": [
            {"data": data}
        ]
    }


def display_value(choices, field, default_field=None):
    options = [When(**{field: k, "then": Value(force_str(v))}) for k, v in choices]
    return Case(*options, default=default_field, output_field=CharField())


def create_type_generated_queries():
    user_generated, system_generated = Q(), Q()
    for category in GrievanceTicket.CATEGORY_CHOICES:
        category_num, category_str = category
        if category_num in GrievanceTicket.MANUAL_CATEGORIES:
            user_generated |= Q(category_name=force_str(category_str))
        else:
            system_generated |= Q(category_name=force_str(category_str))
    return user_generated, system_generated


class BusinessAreaInput(graphene.InputObjectType):
    business_area = graphene.String()


class TicketByType(graphene.ObjectType):
    user_generated_count = graphene.Int()
    system_generated_count = graphene.Int()
    closed_user_generated_count = graphene.Int()
    closed_system_generated_count = graphene.Int()
    user_generated_avg_resolution = graphene.Float()
    system_generated_avg_resolution = graphene.Float()


class TicketByLocationAndCategory(graphene.ObjectType):
    location = graphene.String()
    count = graphene.Int()
    categories = graphene.List(TicketByCategory)

    def resolve_count(self, info):
        return sum([category["count"] for category in self.get("categories")])


class Query(graphene.ObjectType):
    tickets_by_type = graphene.Field(TicketByType, business_area_slug=graphene.String(required=True))
    tickets_by_category = graphene.Field(ChartDatasetNode, business_area_slug=graphene.String(required=True))
    tickets_by_status = graphene.Field(ChartDatasetNode, business_area_slug=graphene.String(required=True))
    tickets_by_location_and_category = graphene.List(
        TicketByLocationAndCategory, business_area_slug=graphene.String(required=True)
    )

    def resolve_tickets_by_type(self, info, **kwargs):
        user_generated, system_generated = create_type_generated_queries()

        return (
            GrievanceTicket.objects
            .filter(business_area__slug=kwargs.get("business_area_slug"))
            .annotate(
                category_name=display_value(GrievanceTicket.CATEGORY_CHOICES, "category"),
                days_diff=F("updated_at__day") - F("created_at__day"),
            )
            .values_list("category_name", "days_diff")
            .aggregate(
                user_generated_count=Count("category_name", filter=user_generated),
                system_generated_count=Count("category_name", filter=system_generated),
                closed_user_generated_count=Count("category_name", filter=user_generated & Q(status=6)),
                closed_system_generated_count=Count("category_name", filter=system_generated & Q(status=6)),
                user_generated_avg_resolution=Avg("days_diff", filter=user_generated),
                system_generated_avg_resolution=Avg("days_diff", filter=system_generated),
            )
        )

    def resolve_tickets_by_category(self, info, **kwargs):
        qs = (
            GrievanceTicket.objects
            .filter(business_area__slug=kwargs.get("business_area_slug"))
            .annotate(category_name=display_value(GrievanceTicket.CATEGORY_CHOICES, "category"))
            .values("category_name")
            .annotate(count=Count("category"))
            .values_list("category_name", "count")
            .order_by("-count")
        )

        return transform_to_chart_dataset(qs)

    def resolve_tickets_by_status(self, info, **kwargs):
        qs = (
            GrievanceTicket.objects
            .filter(business_area__slug=kwargs.get("business_area_slug"))
            .annotate(status_name=display_value(GrievanceTicket.STATUS_CHOICES, "status"))
            .values("status_name")
            .annotate(count=Count("status"))
            .values_list("status_name", "count")
            .order_by("-count")
        )

        return transform_to_chart_dataset(qs)

    def resolve_tickets_by_location_and_category(self, info, **kwargs):
        qs = (
            GrievanceTicket.objects.select_related("admin2")
            .filter(business_area__slug=kwargs.get("business_area_slug"))
            .values_list("admin2__title", "category")
            .annotate(
                category_name=display_value(GrievanceTicket.CATEGORY_CHOICES, "category"),
                count=Count("category")
            )
            .order_by("admin2__title", "-count")
        )

        results = []
        for item in qs:
            location, _, category_name, count = item
            category_item = {"category_name": category_name, "count": count}
            if results and results[-1]["location"] == location:
                results[-1]["categories"].append(category_item)
            else:
                results.append({"location": location, "categories": [category_item]})
        return results
