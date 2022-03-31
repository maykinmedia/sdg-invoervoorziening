from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets

from sdg.api.filters import LocatieFilterSet, LokaleOverheidFilterSet
from sdg.api.serializers import LocatieSerializer, LokaleOverheidSerializer
from sdg.organisaties.models import LokaleOverheid, Lokatie as Locatie


@extend_schema_view(
    list=extend_schema(
        description="Lijst van alle organisaties die catalogi met producten aanbieden.",
        parameters=[
            OpenApiParameter(
                "owmsIdentifier",
                OpenApiTypes.URI,
                description="De identificatie (URI) van de organisatie zoals deze gebruikt op standaarden.overheid.nl",
            ),
            OpenApiParameter(
                "owmsPrefLabel",
                OpenApiTypes.STR,
                description="Het label van de organisatie zoals deze gebruikt op standaarden.overheid.nl",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Organisatie die catalogi met producten aanbiedt."
    ),
)
class LokaleOverheidViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a municipality, retrieved by uuid"""

    lookup_field = "uuid"
    queryset = LokaleOverheid.objects.select_related(
        "ondersteunings_organisatie",
        "organisatie",
    ).prefetch_related(
        "locaties",
        "catalogi",
        "bevoegde_organisaties",
    )
    filterset_class = LokaleOverheidFilterSet
    serializer_class = LokaleOverheidSerializer


@extend_schema_view(
    list=extend_schema(
        description="Lijst van alle locaties waar de bijbehorende organisatie 1 of meer producten aanbiedt."
    ),
    retrieve=extend_schema(
        description="Locatie waar de bijbehorende organisatie 1 of meer producten aanbiedt."
    ),
)
class LocatieViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a location, retrieved by uuid"""

    lookup_field = "uuid"
    queryset = Locatie.objects.select_related("lokale_overheid")
    filterset_class = LocatieFilterSet
    serializer_class = LocatieSerializer
