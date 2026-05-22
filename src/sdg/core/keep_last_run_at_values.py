from contextlib import contextmanager

from django.db import transaction

from django_celery_beat.models import PeriodicTask


@contextmanager
@transaction.atomic
def keep_last_run_at_values():
    periodic_tasks = list(PeriodicTask.objects.values("pk", "last_run_at"))

    try:
        yield
    finally:
        periodic_tasks_list = []

        for tasks in periodic_tasks:
            task = PeriodicTask.objects.get(pk=tasks["pk"])
            task.last_run_at = tasks["last_run_at"]
            periodic_tasks_list.append(task)

        PeriodicTask.objects.bulk_update(periodic_tasks_list, ["last_run_at"])
