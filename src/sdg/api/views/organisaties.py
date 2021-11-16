from rest_framework import viewsets

from sdg.api.filters import LokaleOverheidFilterSet, LokatieFilterSet
from sdg.api.serializers import LokaleOverheidSerializer, LokatieSerializer
from sdg.organisaties.models import LokaleOverheid, Lokatie


class LokaleOverheidViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a municipality, retrieved by uuid"""

    lookup_field = "uuid"
    queryset = LokaleOverheid.objects.all()
    filterset_class = LokaleOverheidFilterSet
    serializer_class = LokaleOverheidSerializer


class LokatieViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a location, retrieved by uuid"""

    lookup_field = "uuid"
    queryset = Lokatie.objects.all()
    filterset_class = LokatieFilterSet
    serializer_class = LokatieSerializer
