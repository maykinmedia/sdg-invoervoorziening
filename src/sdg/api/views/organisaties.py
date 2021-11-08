from rest_framework import viewsets

from sdg.api.mixins import MultipleSerializerMixin
from sdg.api.serializers import (
    LokaleOverheidListSerializer,
    LokaleOverheidSerializer,
    LokatieListSerializer,
    LokatieSerializer,
)
from sdg.organisaties.models import LokaleOverheid, Lokatie


class LokaleOverheidViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """Viewset for a municipality, retrieved by uuid"""

    lookup_field = "uuid"
    queryset = LokaleOverheid.objects.all()
    serializer_classes = {
        "retrieve": LokaleOverheidSerializer,
        "list": LokaleOverheidListSerializer,
    }


class LokatieViewSet(MultipleSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """Viewset for a location, retrieved by uuid"""

    serializer_class = LokatieSerializer
    lookup_field = "uuid"
    queryset = Lokatie.objects.all()
    serializer_classes = {
        "retrieve": LokatieSerializer,
        "list": LokatieListSerializer,
    }
