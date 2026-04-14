import json
import tempfile

from django.test import TestCase

from django_celery_beat.models import IntervalSchedule, PeriodicTask
from freezegun import freeze_time

from ..periodic_tasks_dump import dump_tasks


@freeze_time("2026-01-01T00:00:00Z")
class TestPeriodicTasksDumpTestcase(TestCase):
    def setUp(self):
        super().setUp()
        # The django_celery_beat models are automatically loaded in via core/apps.py
        PeriodicTask.objects.all().delete()
        self.interval = IntervalSchedule.objects.first()

    def test_dump_tasks(self):
        PeriodicTask.objects.create(
            name="test_task",
            task="none_existing_task",
            interval=self.interval,
            enabled=False,
        )

        with (
            tempfile.NamedTemporaryFile() as normal,
            tempfile.NamedTemporaryFile() as production,
        ):
            # create dump
            dump_tasks(normal.name, production.name)

            normal.seek(0)
            production.seek(0)

            normal_data = json.loads(normal.read().decode("utf-8"))
            production_data = json.loads(production.read().decode("utf-8"))

        self.assertEqual(len(normal_data), 1)
        self.assertEqual(len(production_data), 1)

        normal_task_data = normal_data[0]
        production_task_data = production_data[0]

        with self.subTest("only enabled is different"):
            normal_fields = set(normal_task_data["fields"].items())
            production_fields = set(production_task_data["fields"].items())

            self.assertEqual(normal_task_data["pk"], production_task_data["pk"])
            self.assertEqual(normal_task_data["model"], production_task_data["model"])

            # assert that enabled is the only difference
            self.assertFalse(normal_fields == production_fields)
            self.assertEqual(normal_fields - production_fields, {("enabled", False)})

        with self.subTest("normal data"):
            self.assertEqual(
                normal_task_data["model"], "django_celery_beat.periodictask"
            )
            self.assertEqual(
                normal_task_data["fields"],
                {
                    "name": "test_task",
                    "task": "none_existing_task",
                    "enabled": False,
                    "date_changed": "2026-01-01T00:00:00",
                    "interval": self.interval.pk,
                    # default data
                    "args": "[]",
                    "clocked": None,
                    "crontab": None,
                    "description": "",
                    "exchange": None,
                    "expire_seconds": None,
                    "expires": None,
                    "headers": "{}",
                    "kwargs": "{}",
                    "last_run_at": None,
                    "one_off": False,
                    "priority": None,
                    "queue": None,
                    "routing_key": None,
                    "solar": None,
                    "start_time": None,
                    "total_run_count": 0,
                },
            )

        with self.subTest("production data"):
            self.assertEqual(
                production_task_data["model"], "django_celery_beat.periodictask"
            )
            self.assertEqual(
                production_task_data["fields"],
                {
                    "name": "test_task",
                    "task": "none_existing_task",
                    "enabled": True,  # production data is always enabled
                    "date_changed": "2026-01-01T00:00:00",
                    "interval": self.interval.pk,
                    # default data
                    "args": "[]",
                    "clocked": None,
                    "crontab": None,
                    "description": "",
                    "exchange": None,
                    "expire_seconds": None,
                    "expires": None,
                    "headers": "{}",
                    "kwargs": "{}",
                    "last_run_at": None,
                    "one_off": False,
                    "priority": None,
                    "queue": None,
                    "routing_key": None,
                    "solar": None,
                    "start_time": None,
                    "total_run_count": 0,
                },
            )
