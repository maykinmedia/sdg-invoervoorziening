import re

from django.db import migrations, models
from sdg.organisaties.models import Lokatie


def update_existing_opening_times(apps, schema_editor):
    locations = Lokatie.objects.all()

    target_fields = [
        "maandag",
        "dinsdag",
        "woensdag",
        "donderdag",
        "vrijdag",
        "zaterdag",
        "zondag",
    ]
    for location in locations:
        for field in target_fields:
            matched_hours = re.findall(
                r"(\s?[0-9]{1,2}[:.][0-9]{2}(?:\s?-\s?[0-9]{1,2}[:.][0-9]{2}))",
                str(getattr(location, field, "")),
            )
            setattr(location, f"{field}_tmp", matched_hours)
        location.save()


class Migration(migrations.Migration):

    dependencies = [
        ("organisaties", "0004_auto_20211007_1251"),
    ]

    operations = [
        migrations.RunPython(update_existing_opening_times),
    ]
