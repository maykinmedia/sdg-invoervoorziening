from datetime import datetime
from typing import List

from django.conf import settings
from django.core.exceptions import FieldError
from django.utils import timezone

import pytz


def string_to_date(string: str, date_format: str):
    date = datetime.strptime(string, date_format)
    tz = pytz.timezone(getattr(settings, "TIME_ZONE", None))
    return timezone.make_aware(date, tz)


def unpack(item):
    """
    Ensure and return the first item exists if it is a list.
    :returns: The first item of the list, otherwise the object itself.
    """
    if not isinstance(item, list):
        return item

    if len(item) != 1:
        raise FieldError("Cached item list must be equal to 1")

    return item[0]


def get_from_cache(model, name, manager_methods: List = None):
    """
    Check if prefetch/annotate cache is available from the manager.
    If there's nothing, it should be retrieved using manager methods.
    """
    if manager_methods is None:
        manager_methods = []

    cached_name = f"_{name}"
    _cached = getattr(model, cached_name, None)

    if _cached is None:
        queryset = model.__class__.objects.all()

        for method in manager_methods:
            queryset = method(queryset)

        instance = queryset.get(pk=model.pk)

        if not hasattr(instance, cached_name):
            raise Exception(
                f"{cached_name} does not exist on {model.__class__.__name__}, check that the `manager_methods` "
                f"argument is correct. "
            )

        return getattr(instance, name)

    return unpack(_cached) if _cached else None
