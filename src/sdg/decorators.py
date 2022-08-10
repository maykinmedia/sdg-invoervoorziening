from functools import wraps

from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse


def enabled(redirect=False):
    def inner(view_func):
        @wraps(view_func)
        def _check(request, *args, **kwargs):
            if settings.SDG_CMS_ENABLED:
                return view_func(request, *args, **kwargs)
            elif redirect:
                return HttpResponseRedirect(reverse("api:index"))
            else:
                raise Http404

        return _check

    return inner
