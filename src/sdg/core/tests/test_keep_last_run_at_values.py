from datetime import datetime

from django.test import TestCase

from django_celery_beat.models import IntervalSchedule, PeriodicTask

from ..keep_last_run_at_values import keep_last_run_at_values


class KeepLastRanAtValuesTest(TestCase):
    def setUp(self):
        super().setUp()
        # The django_celery_beat models are automatically loaded in via core/apps.py
        PeriodicTask.objects.all().delete()
        self.interval = IntervalSchedule.objects.first()

    def test_keep_values(self):
        task_one = PeriodicTask.objects.create(
            name="test_task_1",
            task="none_existing_task",
            interval=self.interval,
            enabled=True,
            last_run_at=datetime(2026, 2, 1, 12, 30, 0),
        )
        task_two = PeriodicTask.objects.create(
            name="test_task_2",
            task="none_existing_task",
            interval=self.interval,
            enabled=True,
            last_run_at=datetime(2026, 2, 2, 12, 30, 0),
        )
        task_three = PeriodicTask.objects.create(
            name="test_task_3",
            task="none_existing_task",
            interval=self.interval,
            enabled=True,
            last_run_at=datetime(2026, 2, 3, 12, 30, 0),
        )

        with keep_last_run_at_values():
            PeriodicTask.objects.update(last_run_at=datetime.now())

        task_one.refresh_from_db()
        task_two.refresh_from_db()
        task_three.refresh_from_db()

        self.assertEqual(task_one.last_run_at, datetime(2026, 2, 1, 12, 30, 0))
        self.assertEqual(task_two.last_run_at, datetime(2026, 2, 2, 12, 30, 0))
        self.assertEqual(task_three.last_run_at, datetime(2026, 2, 3, 12, 30, 0))
