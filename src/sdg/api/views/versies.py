from django.core.exceptions import ValidationError

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
    list=extend_schema(
        description="""Krijg een lijst met alle product versies te zien.
        """
    ),
    retrieve=extend_schema(
        description="""Krijg een specifieke product versie te zien.
        """,
        parameters=[
            OpenApiParameter(
                name="uuid",
                description="De UUID van het product die u wilt ophalen.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
        ],
    ),
)
class ProductVersieViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    lookup_field = "uuid"
    lookup_url_kwarg = "uuid"

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

    def get_organisatie(self, request, view, obj=None):
        if request.method == "POST":
            print(view.kwargs)
            versies_uuid = view.kwargs["versies_uuid"]
            try:
                product = Product.objects.get(uuid=versies_uuid)
            except Product.DoesNotExist:
                return None
            except ValidationError:
                return None

            return product.catalogus.lokale_overheid.organisatie

        return None


@extend_schema_view(
    create=extend_schema(
        description="""Maak/update een productversie concept. Om de productversie correct aan te maken,moet u in de url het 'productUuid' opgeven.
        """,
        parameters=[
            OpenApiParameter(
                name="versies_uuid",
                description="De UUID van het product die u wilt updaten.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="versie",
                description="Het versie nummer van het product die u wilt updaten.",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            ),
        ],
    ),
)
@extend_schema(
    parameters=[
        OpenApiParameter(
            name="versies_uuid",
            description="De UUID van het product die u wilt updaten.",
            required=True,
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
        ),
    ]
)
class ProductVersieCreateViewSet(
    mixins.CreateModelMixin,
    GenericViewSet,
):
    serializer_class = ProductVersieSingleSerializer
    permission_classes = [OrganizationPermissions, WhitelistedPermission]

    def get_organisatie(self, request, view, obj=None):
        if request.method == "POST":
            versies_uuid = view.kwargs["versies_uuid"]
            try:
                product = Product.objects.get(uuid=versies_uuid)
            except Product.DoesNotExist:
                return None
            except ValidationError:
                return None

            return product.catalogus.lokale_overheid.organisatie

        return None

    @action(
        detail=False,
        methods=["post"],
        serializer_class=ProductVersiePublishSerializer,
    )
    def publish(self, request, *args, **kwargs):
        """
        Publiseer het concept.

        Door het publiseren van het concept krijgt het product de publicatie datum van vandaag de dag.
        Letop een gepubliseerde product kan niet meer worden aangepast, er kan wel een nieuwe product versie worden aangemaakt.
        """

        versies_uuid = kwargs.pop("versies_uuid", None)
        versie = kwargs.pop("versie", None)
        try:
            product = Product.objects.get(uuid=versies_uuid)
        except Product.DoesNotExist:
            raise serializers.ValidationError("De gegeven versies_uuid bestaat niet.")
        except ValidationError:
            raise serializers.ValidationError("De gegeven versies_uuid bestaat niet.")

        try:
            product_versie = ProductVersie.objects.get(product=product, versie=versie)
        except Product.DoesNotExist:
            raise serializers.ValidationError("De gegeven versies_uuid bestaat niet.")
        except ValidationError:
            raise serializers.ValidationError("De gegeven versies_uuid bestaat niet.")

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
    create=extend_schema(
        description="""Update 1 specifieke vertaling van een productversie concept. Om de productversie correct aan te maken,moet u in de url het 'productUuid' opgeven.
        """,
        parameters=[
            OpenApiParameter(
                name="versies_uuid",
                description="De UUID van het product die u wilt updaten.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="versie",
                description="Het versie nummer van het product die u wilt updaten.",
                required=True,
                type=OpenApiTypes.INT,
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
class ProductVersieTranslationCreateViewSet(
    mixins.CreateModelMixin,
    GenericViewSet,
):

    serializer_class = ProductVersieVertalingenSerializer
    permission_classes = [OrganizationPermissions, WhitelistedPermission]

    def get_organisatie(self, request, view, obj=None):
        if request.method == "POST":
            versies_uuid = view.kwargs["versies_uuid"]
            try:
                product = Product.objects.get(uuid=versies_uuid)
            except Product.DoesNotExist:
                return None
            except ValidationError:
                return None

            return product.catalogus.lokale_overheid.organisatie

        return None


@extend_schema_view(
    list=extend_schema(
        description="""Een lijst met alle vertalingen van de specifieke `versie` van een `product`.
        """,
        parameters=[
            OpenApiParameter(
                name="versies_uuid",
                description="De UUID van het `product` die u wilt ophalen.",
                required=True,
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name="versie",
                description="Het versie nummer van het `product` die u wilt ophalen.",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            ),
        ],
    ),
)
class ProductVersieTranslationListViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):

    serializer_class = ProductVersieVertalingenSerializer
    permission_classes = [OrganizationPermissions, WhitelistedPermission]

    def get_queryset(self):
        try:
            return LocalizedProduct.objects.filter(
                product_versie__product__uuid=self.kwargs["versies_uuid"],
                product_versie__versie=self.kwargs["versie"],
            )
        except ValidationError:
            return LocalizedProduct.objects.none()
        except ValueError:
            return LocalizedProduct.objects.none()
        except KeyError:
            return LocalizedProduct.objects.none()

    def get_organisatie(self, request, view, obj=None):
        if request.method == "POST":
            versies_uuid = view.kwargs["versies_uuid"]
            try:
                product = Product.objects.get(uuid=versies_uuid)
            except Product.DoesNotExist:
                return None
            except ValidationError:
                return None

            return product.catalogus.lokale_overheid.organisatie

        return None
