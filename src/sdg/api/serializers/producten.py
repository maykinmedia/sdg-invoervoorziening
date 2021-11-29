from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import HyperlinkedRelatedField

from sdg.api.serializers.fields import LabeledUrlListField
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.models import LocalizedProduct, Product, ProductVersie


class LocalizedProductSerializer(serializers.ModelSerializer):
    """Serializer for the localized version of a product."""

    verwijzing_links = LabeledUrlListField()

    class Meta:
        model = LocalizedProduct
        fields = (
            "taal",
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
            "gemaakt_op",
            "gewijzigd_op",
            "publicatie_datum",
            "vertalingen",
        )


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for a product, including UPN, availability, locations and latest version translations."""

    upn_label = serializers.CharField(source="generic_product.upn_label")
    upn_uri = serializers.URLField(source="generic_product.upn_uri")
    organisatie = HyperlinkedRelatedField(
        source="catalogus.lokale_overheid",
        lookup_field="uuid",
        view_name="api:lokaleoverheid-detail",
        queryset=LokaleOverheid.objects.all(),
    )
    vertalingen = SerializerMethodField(method_name="get_vertalingen")
    versie = SerializerMethodField(method_name="get_versie")

    class Meta:
        model = Product
        fields = (
            "url",
            "uuid",
            "upn_label",
            "upn_uri",
            "versie",
            "organisatie",
            "product_aanwezig",
            "product_aanwezig_toelichting",
            "catalogus",
            "locaties",
            "doelgroep",
            "vertalingen",
            "gerelateerde_producten",
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
            "gerelateerde_producten": {
                "lookup_field": "uuid",
                "view_name": "api:product-detail",
            },
            "locaties": {
                "source": "lokaties",
                "lookup_field": "uuid",
                "view_name": "api:lokatie-detail",
            },
        }

    def get_vertalingen(self, obj: Product) -> LocalizedProductSerializer(many=True):
        _request = self.context["request"]
        vertalingen = getattr(obj.laatste_actieve_versie, "vertalingen", [])

        if taal := _request.query_params.get("taal", None):
            vertalingen = vertalingen.filter(taal=taal)

        return LocalizedProductSerializer(vertalingen, many=True).data

    def get_versie(self, obj: Product) -> int:
        return getattr(obj.laatste_actieve_versie, "versie", 0)
