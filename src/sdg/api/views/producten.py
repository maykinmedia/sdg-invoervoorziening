from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, viewsets
from rest_framework.viewsets import GenericViewSet

from sdg.api.filters import ProductFilterSet
from sdg.api.permissions import Permissions
from sdg.api.serializers import ProductSerializer, ProductVersieSerializer
from sdg.core.models.logius import Overheidsorganisatie
from sdg.producten.models import Product, ProductVersie


@extend_schema_view(
    list=extend_schema(
        description="Lijst van alle producten die voorkomen in de catalogi.",
        auth=[],
        parameters=[
            OpenApiParameter(
                name="catalogus",
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een catalogus om aan te geven van welke catalogus u de producten wilt zien.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="doelgroep",
                description="Hierin vermeld u de gewensde doelgroep om aleen producten met die doelgroep te zien. <br> Opties: `eu-bedrijf` `eu-burger`",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatie",
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een organisatie om aan te geven van welke organisatie u de producten wilt zien.",
                required=False,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsIdentifier",
                description="""Hierin vermeld u de OWMS Identifier (https://standaarden.overheid.nl/owms/4.0/doc/eigenschappen/dcterms.identifier)
                van een organisatie om aan te geven van welke organisatie u de producten wilt zien.""",
                required=False,
                type=OpenApiTypes.URI,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="organisatieOwmsPrefLabel",
                description="Hierin vermeld u de OWMS Prefered Label van een organisatie om aan te geven van welke organisatie u de producten wilt zien.",
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
            OpenApiParameter(
                name="productAanwezig",
                description="Hierin vermeld u een van de drie opties om alleen producten met die specifieke optie te tonen. <br> Opties: `ja` `nee` `onbekend`",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="publicatieDatum",
                description="Hierin vermeld u de publicatie datum om alle producten te zien met die specifieke publicatie datum.",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="publicatieDatum__gte",
                description="Hierin vermeld u de publicatie datum om alle producten te zien met die specifieke publicatie datum of een datum die groter is.",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="taal",
                description="Hierin vermeld u de taal die u wilt zien van de producten.<br> ISO 639-1 (https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) <br> Opties: `en` `nl`",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="upnLabel",
                description="Hier vermeld u de UPN Label (https://standaarden.overheid.nl/owms/4.0/doc/waardelijsten/overheid.uniformeproductnaam) van het product die u wilt zien.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="upnUri",
                description="Hier vermeld u de UPN URI (https://standaarden.overheid.nl/owms/4.0/doc/waardelijsten/overheid.uniformeproductnaam) van het product die u wilt zien.",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="Product dat voorkomt in een catalogus.",
        auth=[],
        parameters=[
            OpenApiParameter(
                "uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een product om aan te geven welke product u wilt zien.",
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
    create=extend_schema(
        description="Maak een nieuwe product versie aan of update een concept voor een catalogus."
    ),
)
class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """Viewset for a product, retrieved by uuid"""

    lookup_field = "uuid"
    queryset = (
        Product.objects.select_related(
            "catalogus",
            "catalogus__lokale_overheid",
            "generiek_product",
            "generiek_product__upn",
        )
        .prefetch_related(
            "gerelateerde_producten",
            "locaties",
            "versies",
            "versies__vertalingen",
        )
        .active()
        .order_by("generiek_product__upn__upn_label")
    )
    filterset_class = ProductFilterSet
    serializer_class = ProductSerializer
    permission_classes = [Permissions]

    def get_organisatie(self, request, view, obj=None):
        if request.method == "POST":
            organisatie = view.request.data.get("verantwoordelijke_organisatie", None)
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

        return None


@extend_schema_view(
    list=extend_schema(
        auth=[],
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een product om aan te geven welke product u wilt zien.",
            ),
            OpenApiParameter(
                name="page",
                description="Hierin kunt u aangeven welke pagina (https://en.wikipedia.org/wiki/Pagination) u wilt zien.",
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


@extend_schema_view(
    list=extend_schema(
        auth=[],
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="Hierin vermeld u de UUID(https://en.wikipedia.org/wiki/Universally_unique_identifier) van een product om aan te geven welke product u wilt zien.",
            ),
            OpenApiParameter(
                name="page",
                description="Hierin kunt u aangeven welke pagina (https://en.wikipedia.org/wiki/Pagination) u wilt zien.",
                required=False,
                type=int,
                location=OpenApiParameter.QUERY,
            ),
        ],
        description="Lijst van concept-productversies voor dit product.",
    ),
)
class ProductConceptViewSet(mixins.ListModelMixin, GenericViewSet):
    """Viewset for the concept version of a product."""

    serializer_class = ProductVersieSerializer
    queryset = ProductVersie.objects.none()

    def get_queryset(self):
        return (
            ProductVersie.objects.filter(publicatie_datum=None)
            .filter(product__uuid=self.kwargs["product_uuid"])
            .prefetch_related("vertalingen")
        )
