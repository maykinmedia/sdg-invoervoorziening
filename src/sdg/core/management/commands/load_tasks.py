from django.core.management.commands import loaddata

from ...keep_last_run_at_values import keep_last_run_at_values


class Command(loaddata.Command):
    def handle(self, *args, **options):
        with keep_last_run_at_values():
            super().handle(*args, **options)
