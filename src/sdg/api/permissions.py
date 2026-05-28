import datetime
import logging

from django.conf import settings

from rest_framework.permissions import BasePermission
from vng_api_common.permissions import bypass_permissions

from sdg.api.models import Token

logger = logging.getLogger(__name__)


def get_client_ip(request):
    real_ip = request.headers.get(settings.CLIENT_IP_HTTP_HEADER)
    if real_ip:
        ip = real_ip
    else:
        ip = request.headers.get("REMOTE_ADDR")
    return ip


class OrganizationPermissions(BasePermission):
    def has_permission(self, request, view):
        if bypass_permissions(request):
            return True

        if view.action in ["list", "retrieve", "option"]:
            return True

        if not request.auth:
            return False

        if view.action in ["update", "destroy"]:
            return True

        organisatie = view.get_organisatie(request, view)

        if not organisatie:
            return False

        if organisatie.pk not in request.auth.tokenauthorization_set.values_list(
            "lokale_overheid__organisatie__pk", flat=True
        ):
            return False

        Token.objects.filter(key=request.auth).update(last_seen=datetime.datetime.now())

        return True

    def has_object_permission(self, request, view, obj):
        if bypass_permissions(request):
            return True

        if view.action == "retrieve":
            return True

        organisatie = view.get_organisatie(request, view, obj)

        if organisatie.pk not in request.auth.tokenauthorization_set.values_list(
            "lokale_overheid__organisatie__pk", flat=True
        ):
            return False

        Token.objects.filter(key=request.auth).update(last_seen=datetime.datetime.now())

        return True


class WhitelistedPermission(BasePermission):
    def has_permission(self, request, view):
        if bypass_permissions(request):
            return True

        if view.action in ["list", "retrieve", "option"]:
            return True

        if settings.SDG_API_WHITELISTING_ENABLED:
            user_ip = get_client_ip(request)
            whitelisted_ips = request.auth.whitelisted_ips

            if not user_ip:
                logger.error("Permission denied: Could not determine IP address.")
                return False

            if not whitelisted_ips:
                logger.warning(
                    "Permission denied: No whitelist provided for API-token: %s",
                    request.auth,
                )
                return False

            if user_ip not in whitelisted_ips:
                logger.info(
                    "Permission denied: IP address %s not in whitelist: %s",
                    user_ip,
                    ", ".join(whitelisted_ips),
                )
                return False

        return True
