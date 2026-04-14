from pathlib import Path

from django.core import serializers

from django_celery_beat.models import PeriodicTask


def dump_tasks(file_path_normal: Path, file_path_production: Path):
    fixture_data = serializers.serialize(
        "json",
        PeriodicTask.objects.all(),
        indent=4,
        use_natural_primary_keys=True,
    )

    with open(file_path_normal, "w") as outfile:
        outfile.write(fixture_data)

    with open(file_path_production, "w") as outfile:
        outfile.write(fixture_data.replace('"enabled": false', '"enabled": true'))
