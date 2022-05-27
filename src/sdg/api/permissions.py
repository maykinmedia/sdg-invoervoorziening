from rest_framework.permissions import SAFE_METHODS, BasePermission
from vng_api_common.permissions import bypass_permissions


class LocationPermission(BasePermission):
    def has_permission(self, request, view):
        if bypass_permissions(request):
            return True

        if request.method in SAFE_METHODS:
            return True

        if not request.auth:
            return False

        if view.action == "create":
            organisatie = view.get_organisatie(request, view)

            if organisatie.get("owms_pref_label"):
                if (
                    request.auth.lokale_overheid.organisatie.owms_pref_label
                    != organisatie.get("owms_pref_label")
                ):
                    return False

            if organisatie.get("owms_identifier"):
                if (
                    request.auth.lokale_overheid.organisatie.owms_identifier
                    != organisatie.get("owms_identifier")
                ):
                    return False

        return True

    def has_object_permission(self, request, view, obj):
        if bypass_permissions(request):
            return True

        organisatie = view.get_organisatie(request, view, obj)

        if view.action == "retrieve":
            return True

        if (
            request.auth.lokale_overheid.organisatie.owms_pref_label
            != organisatie.owms_pref_label
        ):
            return False

        return True
