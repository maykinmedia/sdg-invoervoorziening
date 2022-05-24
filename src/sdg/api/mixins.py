from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

from sdg.api.models import TokenAuthorization


class CreateLocatieMixin(object):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer, request.auth)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer, auth):
        validated_label = serializer.validated_data["lokale_overheid"]["organisatie"][
            "owms_pref_label"
        ]
        validated_organization_token = TokenAuthorization.objects.get(
            lokale_overheid__organisatie__owms_pref_label=validated_label
        ).token

        if validated_organization_token != auth:
            raise exception_handler(status.HTTP_401_UNAUTHORIZED)

        serializer.save()
