from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication as _TokenAuthentication

from .models import TokenAuthorization


class TokenAuthentication(_TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = TokenAuthorization.objects.get(token=key)
        except TokenAuthorization.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token.")

        return (token.lokale_overheid, token)
