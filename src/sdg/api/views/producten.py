from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from sdg.api.filters import ProductFilterSet
from sdg.api.permissions import OrganizationPermissions, WhitelistedPermission
from sdg.api.serializers import ProductSerializer, ProductVersieSerializer
from sdg.core.models.logius import Overheidsorganisatie
from sdg.producten.models import Product, ProductVersie


@extend_schema_view(
    list=extend_schema(
        description="""Lijst van alle (actieve versies van de) producten. Om een enkel product op te halen uit deze lijst kunt u filteren op:

* `upnUri`
* `verantwoordelijkeOrganisatie.owmsIdentifier`
* `doelgroep`

Deze gegevens tezamen vormen de unieke sleutel van een product.""",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="catalogus",
                description="De UUID van een catalogus om aan te geven van welke catalogus u de producten wilt zien.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="doelgroep",
                description="""De gewenste doelgroep om alleen producten met die doelgroep te zien.

Opties: `eu-burger` of `eu-bedrijf`""",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatie",
                description="De UUID van een organisatie om aan te geven van welke organisatie u de producten wilt zien.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsIdentifier",
                description="""De OWMS Identifier
                van een organisatie om aan te geven van welke organisatie u de producten wilt zien.""",
                required=False,
                type=OpenApiTypes.URI,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsPrefLabel",
                description="Het OWMS Prefered Label van een organisatie om aan te geven van welke organisatie u de producten wilt zien.",
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
            OpenApiParameter(
                name="productAanwezig",
                description="""Een van de drie opties om alleen producten met die specifieke optie te tonen.

Opties: `ja`, `nee` of `onbekend`""",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="publicatieDatum",
                description="De publicatie datum om alle producten te zien met die specifieke publicatie datum.",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="publicatieDatum__gte",
                description="De publicatie datum om alle producten te zien met die specifieke publicatie datum of een datum die groter is.",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="taal",
                description="""De vertaling die u wilt zien van de producten. Indien geen taal is opgegeven dan worden all vertalingen getoond. Formaat: ISO 639-1 (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).

Opties: `en` of `nl`""",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="upnLabel",
                description="Het UPN Label van het product dat u wilt zien.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="upnUri",
                description="De UPN URI van het product dat u wilt zien.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Haal een specifieke (actieve versie van het) product op.",
        auth=[],
        parameters=[
            OpenApiParameter(
                "uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="De UUID van een product om aan te geven welke product u wilt zien.",
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
    create=extend_schema(
        description="""Maak een nieuwe productversie aan. Om de productversie correct aan te maken, moet u minimaal
opgeven:

* `upnUri`
* `verantwoordelijkeOrganisatie.owmsIdentifier`
* `doelgroep`

Deze gegevens tezamen vormen de unieke sleutel van een product.

Indien u geen `bevoegdeOrganisatie` opgeeft, dan wordt de `verantwoordelijkeOrganisatie` gebruikt als bevoegde
organisatie. Indien u geen `catalogus` opgeeft, dan wordt de standaard catalogus gebruikt.
"""
    ),
)
class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """Viewset for a product, retrieved by UUID"""

    lookup_field = "uuid"
    queryset = (
        Product.objects.active_organization()
        .select_related(
            "catalogus",
            "catalogus__lokale_overheid",
            "generiek_product",
            "generiek_product__upn",
        )
        .prefetch_related(
            "locaties",
            "versies",
            "versies__vertalingen",
        )
        .active()
        .order_by("generiek_product__upn__upn_label")
        .exclude_generic_status(api=True)
    )
    filterset_class = ProductFilterSet
    serializer_class = ProductSerializer
    permission_classes = [OrganizationPermissions, WhitelistedPermission]

    def get_organisatie(self, request, view, obj=None):
        if request.method == "POST":
            organisatie = view.request.data.get("verantwoordelijke_organisatie", None)
            if not organisatie:
                return None

            if "owms_identifier" in organisatie:
                try:
                    return Overheidsorganisatie.objects.get(
                        owms_identifier=organisatie.get("owms_identifier")
                    )
                except Overheidsorganisatie.DoesNotExist:
                    return None

        return None


@extend_schema_view(
    list=extend_schema(
        auth=[],
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="De UUID van een product om aan te geven welke product u wilt zien.",
            ),
            OpenApiParameter(
                name="page",
                description="Het paginanummer binnen de lijst van resultaten.",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
        description="""Lijst van alle productversies van een product,
        met deze versies kunnen we veranderingen in de teksten documenteren zonder de oude teksten te verliezen.""",
    ),
)
class ProductHistoryViewSet(mixins.ListModelMixin, GenericViewSet):
    """Viewset for the version history of a product."""

    serializer_class = ProductVersieSerializer
    queryset = ProductVersie.objects.none()

    def get_queryset(self):
        return (
            ProductVersie.objects.published()
            .filter(product__uuid=self.kwargs["product_uuid"])
            .prefetch_related("vertalingen")
        )
