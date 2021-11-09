from rest_framework import serializers

from sdg.api.serializers.organisaties import LokatieListSerializer
from sdg.core.models import ProductenCatalogus
from sdg.producten.models import LocalizedProduct, Product, ProductVersie


class LocalizedProductSerializer(serializers.ModelSerializer):
    """Serializer for the localized version of a product."""

    class Meta:
        model = LocalizedProduct
        fields = (
            "product_versie",
            "decentrale_link",
            "specifieke_link",
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
        )


class ProductVersieSerializer(serializers.ModelSerializer):
    """Serializer for the version of a product."""

    vertalingen = LocalizedProductSerializer(many=True)

    class Meta:
        model = ProductVersie
        fields = (
            "versie",
            "gemaakt_door",
            "gemaakt_op",
            "gewijzigd_op",
            "publicatie_datum",
            "vertalingen",
        )


class ProductListSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for a product listing, including UPN information."""

    lokale_overheid = serializers.CharField(source="catalogus.lokale_overheid")

    class Meta:
        model = Product
        fields = (
            "uuid",
            "upn_uri",
            "upn_label",
            "is_referentie_product",
            "lokale_overheid",
        )


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for a product, including UPN, availability, locations and latest version translations."""

    lokale_overheid = serializers.CharField(source="catalogus.lokale_overheid")
    lokaties = LokatieListSerializer(many=True)
    vertalingen = LocalizedProductSerializer(
        source="laatste_actieve_versie.vertalingen", many=True
    )
    referentie_product = ProductListSerializer()
    gerelateerde_producten = ProductListSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "uuid",
            "upn_uri",
            "upn_label",
            "is_referentie_product",
            "lokale_overheid",
            "beschikbaar",
            # "generiek_product",
            "referentie_product",
            "gerelateerde_producten",
            "catalogus",
            "doelgroep",
            "lokaties",
            "vertalingen",
        )
        extra_kwargs = {
            "catalogus": {
                "lookup_field": "uuid",
                "queryset": ProductenCatalogus.objects.all(),
            },
        }
