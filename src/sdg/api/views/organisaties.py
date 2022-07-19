from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets

from sdg.api.filters import LocatieFilterSet, LokaleOverheidFilterSet
from sdg.api.permissions import Permissions
from sdg.api.serializers import LokaleOverheidSerializer
from sdg.api.serializers.organisaties import LocatieSerializer
from sdg.core.models.logius import Overheidsorganisatie
from sdg.organisaties.models import LokaleOverheid, Lokatie as Locatie


@extend_schema_view(
    list=extend_schema(
        description="Een lijst van alle organisaties die gekoppeld zijn aan catalogi met producten.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="owmsIdentifier",
                description="Hierin vermeld u de OWMS Identifier (https://standaarden.overheid.nl/owms/4.0/doc/eigenschappen/dcterms.identifier)  van de organisatie waarvan u de informatie wilt zien.",
                required=False,
                type=OpenApiTypes.URI,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="owmsPrefLabel",
                description="Hierin vermeld u de OWMS Prefered Label van de organisatie waarvan u de informatie wilt zien.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page",
                description="Hierin kunt u aangeven welke pagina (https://en.wikipedia.org/wiki/Pagination) u wilt zien.",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Alle informatie over een specifieke organisatie.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een organisatie om aan te geven welke organisatie u wilt zien.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
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
        description="Lijst van alle locaties waar de bijbehorende organisatie 1 of meer producten aanbiedt.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="organisatie",
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsIdentifier",
                description="""Hierin vermeld u de OWMS Identifier (https://standaarden.overheid.nl/owms/4.0/doc/eigenschappen/dcterms.identifier)
                van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.""",
                required=False,
                type=OpenApiTypes.URI,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsPrefLabel",
                description="Hierin vermeld u de OWMS Prefered Label van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page",
                description="Hierin kunt u aangeven welke pagina (https://en.wikipedia.org/wiki/Pagination) u wilt zien.",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Locatie waar de bijbehorende organisatie 1 of meer producten aanbiedt.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
    ),
    create=extend_schema(description="Maak een nieuwe locatie voor een organisatie."),
    update=extend_schema(
        description="Update de locatie van een organistatie.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
    ),
    partial_update=extend_schema(
        description="Update de locatie van een organistatie.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
    ),
    destroy=extend_schema(
        description="Verweider de locatie van een organisatie",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
    ),
)
class LocatieViewSet(viewsets.ModelViewSet):
    """Viewset for a location, retrieved by uuid"""

    lookup_field = "uuid"
    queryset = Locatie.objects.select_related("lokale_overheid")
    filterset_class = LocatieFilterSet
    serializer_class = LocatieSerializer
    permission_classes = [Permissions]

    def get_organisatie(self, request, view, obj=None):
        if request.method == "POST":
            organisatie = view.request.data.get("organisatie", None)
            if not organisatie:
                return None

            for field in ["owms_pref_label", "owms_identifier"]:
                if field in organisatie:
                    try:
                        return Overheidsorganisatie.objects.get(
                            **{field: organisatie.get(field)}
                        )
                    except Overheidsorganisatie.DoesNotExist:
                        return None

        if obj is None:
            return None

        return obj.lokale_overheid.organisatie
