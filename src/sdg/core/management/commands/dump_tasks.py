from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from ...periodic_tasks_dump import dump_tasks


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            "--file-path-normal",
            action="store",
            help=(
                "The file path to where the fixture file will be created."
                "This fixture file will reflect the database 1-1."
            ),
            default=Path(
                Path(settings.DJANGO_PROJECT_DIR) / "fixtures" / "periodic_tasks.json",
            ),
        )

        parser.add_argument(
            "--file-path-production",
            action="store",
            help=(
                "The file path to where the fixture file will be created."
                "This fixture file forces all tasks to be enabled by default."
            ),
            default=Path(
                Path(settings.DJANGO_PROJECT_DIR)
                / "fixtures"
                / "periodic_tasks_production.json",
            ),
        )

    def handle(self, **options):
        file_path_normal = options["file_path_normal"]
        if not isinstance(file_path_normal, Path):
            file_path_normal = Path(file_path_normal)

        file_path_production = options["file_path_production"]
        if not isinstance(file_path_production, Path):
            file_path_production = Path(file_path_production)

        dump_tasks(
            file_path_normal=file_path_normal, file_path_production=file_path_production
        )
