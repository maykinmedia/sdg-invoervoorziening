from django.contrib.auth.models import AnonymousUser

from rest_framework.authentication import TokenAuthentication as _TokenAuthentication

from sdg.api.models import Token


class TokenAuthentication(_TokenAuthentication):
    """Custom token authentication without user binding."""

    model = Token

    def authenticate_credentials(self, key):
        """Authenticate credentials without user checking."""
        anon, model = AnonymousUser(), self.get_model()

        try:
            token = model.objects.get(key=key)
            return anon, token
        except model.DoesNotExist:
            return anon, None  # optional
