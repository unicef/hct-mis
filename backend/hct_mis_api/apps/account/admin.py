from django.contrib import admin

from account.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
