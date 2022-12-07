from django.core.exceptions import ValidationError
from django.http import Http404

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from sdg.api.permissions import OrganizationPermissions, WhitelistedPermission
from sdg.api.serializers.versies import (
    ProductVersiePublishSerializer,
    ProductVersieSingleSerializer,
    ProductVersieVertalingenSerializer,
)
from sdg.core.constants.product import TaalChoices
from sdg.producten.models import Product, ProductVersie
from sdg.producten.models.localized import LocalizedProduct


@extend_schema_view(
    publiceren=extend_schema(
        description="""Publiceer de product versie met de bijgewerkte vertalingen doormiddel van:
        `product_uuid`, `versie`
        """,
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="De UUID van een product om aan te geven welke product u wilt publiceren.",
            ),
            OpenApiParameter(
                name="versie",
                description="Het versie nummer van het product die u wilt publiceren.",
                required=True,
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.PATH,
            ),
        ],
    ),
    list=extend_schema(
        description="""Krijg een lijst met alle product versies te zien.
        """,
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="De UUID van een product om aan te geven welke product u wilt ophalen.",
            ),
        ],
    ),
    retrieve=extend_schema(
        description="""Krijg een specifieke product versie te zien.
        """,
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="De UUID van een product om aan te geven welke product u wilt ophalen.",
            ),
            OpenApiParameter(
                name="versie",
                description="Het versie nummer van het product die u wilt ophalen.",
                required=True,
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.PATH,
            ),
        ],
    ),
    create=extend_schema(
        description="""Maak een nieuwe product versie aan of update een nog niet gepubliceerde product.
        """,
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="De UUID van een het product waar u een nieuwe versie van aan wilt maken of bewerken.",
            ),
        ],
    ),
)
class ProductVersiesViewset(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    lookup_field = "versie"
    lookup_url_kwarg = "versie"

    serializer_class = ProductVersieSingleSerializer
    permission_classes = [OrganizationPermissions, WhitelistedPermission]
    queryset = (
        Product.objects.select_related(
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
    )

    def get_object(self):
        product_uuid = self.kwargs["product_uuid"]
        version = self.kwargs["versie"]

        if self.request.method == "RETRIEVE":
            try:
                return Product.object.get(uuid=product_uuid, versies=version)
            except Product.DoesNotExist:
                raise Http404

    def get_organisatie(self, request, view, obj=None):
        if request.method == "POST":
            product_uuid = view.kwargs["product_uuid"]
            try:
                product = Product.objects.get(uuid=product_uuid)
            except Product.DoesNotExist:
                return None
            except ValidationError:
                return None

            return product.catalogus.lokale_overheid.organisatie

        return None

    @action(
        detail=False,
        methods=["post"],
        url_path=r"(?P<versie>[0-9]+)/publiceer",
        serializer_class=ProductVersiePublishSerializer,
    )
    def publiceren(self, request, product_uuid=None, versie=None):
        """
        Publiseer het concept.

        Door het publiseren van het concept krijgt het product de publicatie datum van vandaag de dag.
        Letop een gepubliseerde product kan niet meer worden aangepast, er kan wel een nieuwe product versie worden aangemaakt.
        """

        try:
            product = Product.objects.get(uuid=product_uuid)
        except Product.DoesNotExist:
            raise serializers.ValidationError("De gegeven product_uuid bestaat niet.")
        except ValidationError:
            raise serializers.ValidationError("De gegeven product_uuid bestaat niet.")

        try:
            product_versie = ProductVersie.objects.get(product=product, versie=versie)
        except Product.DoesNotExist:
            raise serializers.ValidationError("De gegeven product_uuid bestaat niet.")
        except ValidationError:
            raise serializers.ValidationError("De gegeven product_uuid bestaat niet.")

        serializer = ProductVersiePublishSerializer(
            product_versie,
            context={
                "request": request,
                "product": product,
                "product_versie": product_versie,
            },
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        create_data = serializer.create(
            serializer.validated_data,
        )
        headers = self.get_success_headers(create_data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_success_headers(self, data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


@extend_schema_view(
    list=extend_schema(
        description="""Haal alle product vertalingen doormiddle van:
        `product_uuid`, `versie`
        """,
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="De UUID van een product om aan te geven welke product u wilt ophalen.",
            ),
            OpenApiParameter(
                name="versie",
                description="Het versie nummer van het product die u wilt ophalen.",
                required=True,
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.PATH,
            ),
        ],
    ),
    retrieve=extend_schema(
        description="""Haal de specifieke producten vertaling doormiddle van:
        `product_uuid`, `versie`, `taal`
        """,
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="De UUID van een product om aan te geven welke product u wilt ophalen.",
            ),
            OpenApiParameter(
                name="versie",
                description="Het versie nummer van het product die u wilt ophalen.",
                required=True,
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="taal",
                description="De taal van de text die u wilt ophalen.",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                enum=TaalChoices.labels,
            ),
        ],
    ),
    update=extend_schema(
        description="""Update 1 specifieke vertaling van een productversie concept. Om de productversie correct aan te maken, moet u in de url het 'productUuid' opgeven.
        """,
        parameters=[
            OpenApiParameter(
                "product_uuid",
                OpenApiTypes.UUID,
                OpenApiParameter.PATH,
                description="De UUID van het product die u wilt bewerken.",
            ),
            OpenApiParameter(
                name="versie",
                description="Het versie nummer van het product die u wilt bewerken.",
                required=True,
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="taal",
                description="De taal van de tekst die u wilt updaten.",
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                enum=TaalChoices.labels,
            ),
        ],
    ),
)
class ProductVersiesTranslationViewset(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):

    serializer_class = ProductVersieVertalingenSerializer
    permission_classes = [OrganizationPermissions, WhitelistedPermission]

    lookup_field = "taal"
    lookup_url_kwarg = "taal"
    http_method_names = ["get", "retrieve", "put"]
    queryset = LocalizedProduct.objects.none()

    def get_queryset(self):
        product_uuid = self.kwargs["product_uuid"]
        version = self.kwargs["versie"]

        try:
            product = Product.objects.get(uuid=product_uuid)
        except Product.DoesNotExist:
            raise Http404
        try:
            product_versie = ProductVersie.objects.get(product=product, versie=version)
        except ProductVersie.DoesNotExist:
            raise Http404

        try:
            return LocalizedProduct.objects.filter(product_versie=product_versie)
        except LocalizedProduct.DoesNotExist:
            raise Http404

    def get_object(self):
        product_uuid = self.kwargs["product_uuid"]
        version = self.kwargs["versie"]
        taal = self.kwargs["taal"]

        try:
            product = Product.objects.get(uuid=product_uuid)
        except Product.DoesNotExist:
            raise Http404
        try:
            product_versie = ProductVersie.objects.get(product=product, versie=version)
        except ProductVersie.DoesNotExist:
            raise Http404

        try:
            return LocalizedProduct.objects.get(
                product_versie=product_versie, taal=taal
            )
        except LocalizedProduct.DoesNotExist:
            raise Http404

    def get_organisatie(self, request, view, obj=None):
        print(view.kwargs["product_uuid"])

        product_uuid = view.kwargs["product_uuid"]
        try:
            product = Product.objects.get(uuid=product_uuid)
        except Product.DoesNotExist:
            return None
        except ValidationError:
            return None

        return product.catalogus.lokale_overheid.organisatie
