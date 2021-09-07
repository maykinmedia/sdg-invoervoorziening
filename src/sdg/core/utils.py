from dataclasses import dataclass
from datetime import datetime

from django.conf import settings
from django.utils import timezone

import pytz


def string_to_date(string: str, date_format: str):
    date = datetime.strptime(string, date_format)
    tz = pytz.timezone(getattr(settings, "TIME_ZONE", None))
    return timezone.make_aware(date, tz)
