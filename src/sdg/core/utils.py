from datetime import datetime

import pytz
from django.conf import settings
from django.utils import timezone


def string_to_date(string, date_format):
    date = datetime.strptime(string, date_format)
    tz = pytz.timezone(getattr(settings, "TIME_ZONE", None))
    return timezone.make_aware(date, tz)
