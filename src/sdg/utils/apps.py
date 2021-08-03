from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = "sdg.utils"

    def ready(self):
        from . import checks  # noqa
