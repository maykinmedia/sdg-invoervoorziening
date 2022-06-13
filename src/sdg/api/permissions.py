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

        if view.action is "create":
            organisatie = view.get_organisatie(request, view)

            if not organisatie:
                return False

            if organisatie.pk not in request.auth.tokenauthorization_set.values_list(
                "lokale_overheid__organisatie__pk", flat=True
            ):
                return False

        return True

    def has_object_permission(self, request, view, obj):
        if bypass_permissions(request):
            return True

        organisatie = view.get_organisatie(request, view, obj)

        if view.action is "retrieve":
            return True

        if organisatie.pk not in request.auth.tokenauthorization_set.values_list(
            "lokale_overheid__organisatie__pk", flat=True
        ):
            return False

        return True
