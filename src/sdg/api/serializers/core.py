from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from sdg.api.serializers.organisaties import LokaleOverheidBaseSerializer
from sdg.api.serializers.producten import ProductBaseSerializer
from sdg.core.models import ProductenCatalogus


class ProductenCatalogusSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for ProductenCatalogus details, including organizations and products."""

    organisatie = LokaleOverheidBaseSerializer(
        source="lokale_overheid", help_text="De organisatie die deze catalogus beheert."
    )
    producten = serializers.SerializerMethodField(
        help_text="Alle producten binnen deze catalogus.",
    )

    class Meta:
        model = ProductenCatalogus
        fields = (
            "url",
            "uuid",
            "domein",
            "naam",
            "organisatie",
            "is_referentie_catalogus",
            "referentie_catalogus",
            "toelichting",
            "versie",
            "producten",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:productencatalogus-detail",
                "lookup_field": "uuid",
                "help_text": "De unieke URL van dit object binnen deze API.",
            },
            "uuid": {"help_text": "De UUID van de specifieke catalogus"},
            "domein": {
                "help_text": "Een afkorting die wordt gebruikt om het domein aan te duiden."
            },
            "naam": {"help_text": "De naam van de catalogus"},
            "is_referentie_catalogus": {
                "help_text": "Een boolean die aangeeft of de catalogus een referentie catalogus betreft. Een referentie catalogus bevat geen echte productbeschrijvingen."
            },
            "referentie_catalogus": {
                "lookup_field": "uuid",
                "view_name": "api:productencatalogus-detail",
                "help_text": "De URL van de referentieproductcatalogus waar deze productcatalogus aan gekoppeld is",
            },
            "toelichting": {
                "help_text": "Hierin staat de beschreven waar deze catalogus voor dient."
            },
            "versie": {
                "help_text": "De versie van deze catalogus. Op dit moment heeft de waarde geen betekenis."
            },
        }

    @extend_schema_field(ProductBaseSerializer(many=True))
    def get_producten(self, obj):
        queryset = (
            obj.producten.filter(api_verborgen=False)
            .select_related(
                "generiek_product",
                "generiek_product__upn",
            )
            .order_by("generiek_product__upn__upn_label")
            .exclude_generic_status(api=True)
            .distinct()
        )

        request = self.context["request"]

        if request.auth and request.auth.api_default_most_recent:
            queryset = queryset.most_recent()
        else:
            # We need to explicitly exclude active products, otherwise we get
            # a list of all products, of which some have 0 active product
            # versions.
            queryset = queryset.active(exclude_inactive_products=True)

        return ProductBaseSerializer(
            queryset, many=True, read_only=True, context={"request": request}
        ).data
