from rest_framework.authentication import TokenAuthentication as _TokenAuthentication


class TokenAuthentication(_TokenAuthentication):
    """Custom token authentication without user binding."""

    def authenticate_credentials(self, key):
        """Authenticate credentials without user checking."""
        from django.contrib.auth.models import AnonymousUser

        from sdg.api.models import Token

        anon, model = AnonymousUser(), Token

        try:
            token = model.objects.get(key=key)
            return anon, token
        except model.DoesNotExist:
            return anon, None  # optional
