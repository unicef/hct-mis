from django.apps import AppConfig


class Config(AppConfig):
    name = "hct_mis_api.apps.power_query"

    def ready(self):
        from . import tasks

