from django.apps import AppConfig, apps
from django.contrib.contenttypes.management import create_contenttypes
from django.core.management import call_command
from django.db.models.signals import post_migrate


def register_project_models(sender, **kwargs):
    """Make sure project models are registered."""
    project_name = __name__.split(".")[0]

    for app_config in apps.get_app_configs():
        if app_config.name.startswith(project_name):
            create_contenttypes(app_config)


def load_app_fixtures(sender, **kwargs):
    """Clean up and load data for apps."""
    from django.contrib.contenttypes.models import ContentType

    for app_name in sender.fixture_apps:
        app_models = apps.get_app_config(app_name).get_models()

        for AppModel in app_models:
            if not issubclass(AppModel, ContentType):  # Avoid deleting contenttypes
                AppModel.objects.all().delete()

        call_command("loaddata", app_name, verbosity=0)


class CoreConfig(AppConfig):
    name = "sdg.core"
    fixture_apps = [
        "admin_index",
        "django_celery_beat",
    ]

    def ready(self):
        from .checks import localized_form_field_check  # noqa

        post_migrate.connect(register_project_models, sender=self)
        post_migrate.connect(load_app_fixtures, sender=self)
