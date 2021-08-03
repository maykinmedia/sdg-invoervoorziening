from django.views.csrf import csrf_failure as original_csrf_failure, CSRF_FAILURE_TEMPLATE_NAME
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings


def csrf_failure(request, reason="", template_name=CSRF_FAILURE_TEMPLATE_NAME): # Taiga VIPS 1821
    if request.path == reverse('login') and request.user.is_authenticated:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    return original_csrf_failure(request, reason=reason, template_name=template_name)
