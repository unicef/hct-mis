import django.contrib.admin
from django.contrib.admin.apps import AppConfig

from smart_admin.apps import SmartConfig
from smart_admin.decorators import smart_register


class TemplateConfig(AppConfig):
    name = "hct_mis_api.apps.administration"


class Config(SmartConfig):
    default_site = "hct_mis_api.apps.administration.site.HopeAdminSite"
    # verbose_name = _("Smart Admin")
    # name = 'django.contrib.admin'

    def ready(self):
        super().ready()
        django.contrib.admin.autodiscover()
        self.module.autodiscover()
        from django.contrib.admin.models import LogEntry
        from django.contrib.contenttypes.models import ContentType

        from smart_admin.smart_auth.admin import ContentTypeAdmin

        from .admin import LogEntryAdmin

        smart_register(ContentType)(ContentTypeAdmin)
        smart_register(LogEntry)(LogEntryAdmin)

        from django.contrib.admin import site

        from smart_admin.console import (
            panel_error_page,
            panel_migrations,
            panel_redis,
            panel_sentry,
            panel_sysinfo,
        )

        from .panels import email

        site.register_panel(panel_migrations)
        site.register_panel(panel_sysinfo)
        site.register_panel(email)
        site.register_panel(panel_sentry)
        site.register_panel(panel_error_page)
        site.register_panel(panel_redis)
