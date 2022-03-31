from datetime import date

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from sdg.api.serializers.fields import LabeledUrlListField
from sdg.api.serializers.organisaties import (
    BevoegdeOrganisatieSerializer,
    LocatieBaseSerializer,
    LokaleOverheidBaseSerializer,
)
from sdg.producten.models import LocalizedProduct, Product, ProductVersie


class LocalizedProductSerializer(serializers.ModelSerializer):
    """Serializer for the localized version of a product."""

    verwijzing_links = LabeledUrlListField()

    class Meta:
        model = LocalizedProduct
        fields = (
            "taal",
            "specifieke_tekst",
            "bewijs",
            "bezwaar_en_beroep",
            "decentrale_procedure_link",
            "kosten_en_betaalmethoden",
            "procedure_beschrijving",
            "product_titel_decentraal",
            "uiterste_termijn",
            "vereisten",
            "verwijzing_links",
            "wtd_bij_geen_reactie",
            "datum_wijziging",
            "product_valt_onder_toelichting",
        )


class ProductVersieSerializer(serializers.ModelSerializer):
    """Serializer for the version of a product."""

    vertalingen = LocalizedProductSerializer(many=True)

    class Meta:
        model = ProductVersie
        fields = (
            "versie",
            "gemaakt_op",
            "gewijzigd_op",
            "publicatie_datum",
            "vertalingen",
        )


class ProductBaseSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer that exposes a small subset of the fields for a Product, used in references to a product.
    Fields: `url`, `upnUri`, `upnLabel`
    """

    upn_label = serializers.CharField(source="generic_product.upn_label")
    upn_uri = serializers.URLField(source="generic_product.upn_uri")

    class Meta:
        model = Product
        fields = ("url", "upn_uri", "upn_label")
        extra_kwargs = {
            "url": {
                "view_name": "api:product-detail",
                "lookup_field": "uuid",
            }
        }


class ProductSerializer(ProductBaseSerializer):
    """Serializer for a product, including UPN, availability, locations and latest version translations."""

    verantwoordelijke_organisatie = LokaleOverheidBaseSerializer(
        source="catalogus.lokale_overheid"
    )
    publicatie_datum = SerializerMethodField(method_name="get_publicatie_datum")
    vertalingen = SerializerMethodField(method_name="get_vertalingen")
    versie = SerializerMethodField(method_name="get_versie")
    doelgroep = SerializerMethodField(method_name="get_doelgroep")
    gerelateerde_producten = ProductBaseSerializer(many=True)
    locaties = LocatieBaseSerializer(many=True)
    bevoegde_organisatie = BevoegdeOrganisatieSerializer()

    class Meta:
        model = Product
        fields = (
            "url",
            "uuid",
            "upn_label",
            "upn_uri",
            "versie",
            "publicatie_datum",
            "verantwoordelijke_organisatie",
            "product_aanwezig",
            "product_aanwezig_toelichting",
            "catalogus",
            "locaties",
            "doelgroep",
            "vertalingen",
            "referentie_product",
            "gerelateerde_producten",
            "product_valt_onder",
            "bevoegde_organisatie",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:product-detail",
                "lookup_field": "uuid",
            },
            "catalogus": {
                "lookup_field": "uuid",
                "view_name": "api:productencatalogus-detail",
            },
            "referentie_product": {
                "lookup_field": "uuid",
                "view_name": "api:product-detail",
            },
            "product_valt_onder": {
                "lookup_field": "uuid",
                "view_name": "api:product-detail",
            },
        }

    @staticmethod
    def _get_active_field(product: Product, field_name, default=None):
        """Get the value of a field from the product's active version."""
        active_version = getattr(product, "active_version", None)
        return getattr(active_version, field_name) if active_version else default

    def get_vertalingen(self, obj: Product) -> LocalizedProductSerializer(many=True):
        translations = self._get_active_field(obj, "vertalingen", default=[])

        if translations and getattr(obj, "_filter_taal", None):
            translations = [i for i in translations.all() if i.taal == obj._filter_taal]

        return LocalizedProductSerializer(translations, many=True).data

    def get_versie(self, obj: Product) -> int:
        return self._get_active_field(obj, "versie", default=0)

    def get_publicatie_datum(self, obj: Product) -> date:
        return self._get_active_field(obj, "publicatie_datum")

    def get_doelgroep(self, obj: Product) -> str:
        return obj.generic_product.doelgroep
