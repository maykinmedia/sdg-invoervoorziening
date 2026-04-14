from io import StringIO

from django.apps import AppConfig, apps
from django.conf import settings
from django.contrib.contenttypes.management import create_contenttypes
from django.core.management import call_command
from django.db.models.signals import post_migrate


def update_admin_index(sender, **kwargs):
    from django_admin_index.models import AppGroup

    AppGroup.objects.all().delete()

    for app_config in apps.get_app_configs():
        if app_config.name.startswith("sdg"):
            create_contenttypes(app_config, verbosity=0)

    call_command("loaddata", "admin_index", verbosity=0, stdout=StringIO())


def update_cron_jobs(sender, **kwargs):
    call_command("loaddata", "django_celery_beat", verbosity=0, stdout=StringIO())
    call_command(
        "loaddata", settings.PERIODIC_TASKS_FIXTURE, verbosity=0, stdout=StringIO()
    )


class CoreConfig(AppConfig):
    name = "sdg.core"

    def ready(self):
        from .checks import localized_form_field_check

        post_migrate.connect(update_admin_index, sender=self)
        post_migrate.connect(update_cron_jobs, sender=self)
