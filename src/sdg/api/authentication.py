from django.utils.translation import gettext as _

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication as _TokenAuthentication


class TokenAuthentication(_TokenAuthentication):
    """Custom token authentication without user binding."""

    def authenticate_credentials(self, key):
        """Authenticate credentials without user checking."""
        from django.contrib.auth.models import AnonymousUser

        from sdg.api.models import Token

        anon = AnonymousUser()

        if key:
            try:
                token = Token.objects.get(key=key)
                # Authenticated token
                return anon, token
            except Token.DoesNotExist:
                # Invalid token
                raise exceptions.AuthenticationFailed(
                    _("Ongeldig token. Controleer uw token en probeer het opnieuw.")
                )

        # Anonymous usage
        return anon, None
