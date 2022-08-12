import datetime

from rest_framework.permissions import SAFE_METHODS, BasePermission
from vng_api_common.permissions import bypass_permissions

from sdg.api.models import Token


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[-1].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
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

        user_ip = get_client_ip(request)
        whitelisted_ips = request.auth.whitelisted_ips

        if whitelisted_ips:
            if user_ip not in whitelisted_ips:
                return False

        return True
