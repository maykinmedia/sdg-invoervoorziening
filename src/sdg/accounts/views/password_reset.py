import json
from datetime import datetime

from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from sdg.utils.mixins import IPThrottleMixin

from sdg.accounts.models import UserInvitation


class PasswordResetView(IPThrottleMixin, auth_views.PasswordResetView):
    throttle_name = "password-reset"
    throttle_visits = 5
    throttle_period = 60
    throttle_methods = ["get"]


def ResendInventation(request):
    if request.method == "POST":
        body = json.loads(request.body)
        invitation = UserInvitation.objects.get(pk=body.get("pk"))
        if invitation.accepted:
            return HttpResponse(status=204)

        invitation.send_invitation(request)

        invitation.sent = datetime.now()
        invitation.save()

    return HttpResponse(status=200)
