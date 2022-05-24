from rest_framework import permissions

from vng_api_common.permissions import bypass_permissions

from sdg.api.models import TokenAuthorization


class LocationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if bypass_permissions(request):
            return True

        if not request.auth:
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        key = TokenAuthorization.objects.get(lokale_overheid=obj.lokale_overheid).token

        if request.auth == key:
            return True

        return False
