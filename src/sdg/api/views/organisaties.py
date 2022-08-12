from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets

from sdg.api.filters import LocatieFilterSet, LokaleOverheidFilterSet
from sdg.api.permissions import OrganizationPermissions, WhitelistedPermission
from sdg.api.serializers import LokaleOverheidSerializer
from sdg.api.serializers.organisaties import LocatieSerializer
from sdg.core.models.logius import Overheidsorganisatie
from sdg.organisaties.models import LokaleOverheid, Lokatie as Locatie


@extend_schema_view(
    list=extend_schema(
        description="Een lijst van alle organisaties.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="owmsIdentifier",
                description="De OWMS Identifier  van de organisatie waarvan u de informatie wilt zien.",
                required=False,
                type=OpenApiTypes.URI,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="owmsPrefLabel",
                description="Het OWMS Prefered Label van de organisatie waarvan u de informatie wilt zien.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page",
                description="Het paginanummer binnen de lijst van resultaten.",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Een organisatie die verantwoordelijk of bevoegd is voor één of meerdere producten.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="De UUID van een organisatie.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
    ),
)
class LokaleOverheidViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for a municipality, retrieved by UUID"""

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
        description="Lijst van alle locaties.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="organisatie",
                description="De UUID van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsIdentifier",
                description="""De OWMS Identifier
                van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.""",
                required=False,
                type=OpenApiTypes.URI,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsPrefLabel",
                description="Het OWMS Prefered Label van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="page",
                description="Het paginanummer binnen de lijst van resultaten.",
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
                description="De UUID van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
    ),
    create=extend_schema(
        description="Maak een nieuwe locatie voor een organisatie aan."
    ),
    update=extend_schema(
        description="Update de locatie van een organistatie.",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="De UUID van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
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
                description="De UUID van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
    ),
    destroy=extend_schema(
        description="Verwijder de locatie van een organisatie",
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="De UUID van een organisatie om aan te geven van welke organisatie u de locaties wilt zien.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            )
        ],
    ),
)
class LocatieViewSet(viewsets.ModelViewSet):
    """Viewset for a location, retrieved by UUID"""

    lookup_field = "uuid"
    queryset = Locatie.objects.select_related("lokale_overheid")
    filterset_class = LocatieFilterSet
    serializer_class = LocatieSerializer
    permission_classes = [OrganizationPermissions, WhitelistedPermission]

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
