import json
from datetime import datetime

from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.views.generic import View

from sdg.accounts.models import UserInvitation
from sdg.utils.mixins import IPThrottleMixin


class PasswordResetView(IPThrottleMixin, auth_views.PasswordResetView):
    throttle_name = "password-reset"
    throttle_visits = 5
    throttle_period = 60
    throttle_methods = ["get"]


class ResendInventation(PermissionRequiredMixin, View):
    permission_required = "is_staff"

    def post(self, request):
        body = json.loads(request.body)
        invitation = UserInvitation.objects.get(pk=body.get("pk"))
        if invitation.accepted:
            return HttpResponse(status=204)

        invitation.send_invitation(request)

        invitation.sent = datetime.now()
        invitation.save()

        return HttpResponse(status=200)
