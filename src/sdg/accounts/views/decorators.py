from functools import wraps

from django.core.exceptions import PermissionDenied

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.accounts.utils import user_has_valid_roles


def municipality_role_required(roles):
    """Decorator for municipality views that require at least one role."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view, *args, **kwargs):
            if not user_has_valid_roles(
                view.request.user,
                municipality=view.get_lokale_overheid(),
                required_roles=roles,
            ):
                raise PermissionDenied(
                    OverheidRoleRequiredMixin.permission_denied_message
                )
            return view_func(view, *args, **kwargs)

        return _wrapped_view

    return decorator
