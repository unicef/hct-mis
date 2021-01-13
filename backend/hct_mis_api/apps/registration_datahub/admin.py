from django.contrib import admin

from hct_mis_api.apps.registration_datahub.models import (
    RegistrationDataImportDatahub,
    ImportedIndividual,
    ImportedHousehold,
    ImportedDocumentType,
    ImportedDocument,
    ImportData,
    ImportedIndividualRoleInHousehold,
    ImportedIndividualIdentity,
)


@admin.register(RegistrationDataImportDatahub)
class RegistrationDataImportDatahubAdmin(admin.ModelAdmin):
    pass


@admin.register(ImportedIndividual)
class ImportedIndividualAdmin(admin.ModelAdmin):
    pass


@admin.register(ImportedIndividualIdentity)
class ImportedIndividualIdentityAdmin(admin.ModelAdmin):
    pass


@admin.register(ImportedHousehold)
class ImportedHouseholdAdmin(admin.ModelAdmin):
    pass


@admin.register(ImportData)
class ImportDataAdmin(admin.ModelAdmin):
    pass


@admin.register(ImportedDocument)
class ImportedDocumentAdmin(admin.ModelAdmin):
    list_display = ("document_number", "type", "individual")


@admin.register(ImportedDocumentType)
class ImportedDocumentTypeAdmin(admin.ModelAdmin):
    list_display = ("label", "country")


@admin.register(ImportedIndividualRoleInHousehold)
class ImportedIndividualRoleInHouseholdAdmin(admin.ModelAdmin):
    pass
