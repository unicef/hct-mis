from django.contrib import admin

from hct_mis_api.apps.household.models import (
    Household,
    Individual,
    DocumentType,
    Document,
    Agency,
    IndividualRoleInHousehold,
    IndividualIdentity,
)


@admin.register(Agency)
class AgencyTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "type")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("document_number", "type", "individual")


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "country")


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ("id", "size", "country", "head_of_household")


@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    list_display = (
        "given_name",
        "family_name",
        "sex",
        "relationship",
        "birth_date",
    )


@admin.register(IndividualRoleInHousehold)
class IndividualRoleInHouseholdAdmin(admin.ModelAdmin):
    pass


@admin.register(IndividualIdentity)
class IndividualIdentityAdmin(admin.ModelAdmin):
    pass
