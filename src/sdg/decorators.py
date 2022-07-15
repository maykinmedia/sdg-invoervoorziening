from functools import wraps

from django.conf import settings
from django.http import Http404


def enabled(view_func):
    @wraps(view_func)
    def _check(request, *args, **kwargs):
        if settings.SDG_CMS_ENABLED:
            return view_func(request, *args, **kwargs)
        else:
            raise Http404

    return _check
