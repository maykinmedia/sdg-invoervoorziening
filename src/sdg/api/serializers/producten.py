from django.db import transaction

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.reverse import reverse

from sdg.api.serializers.fields import LabeledUrlListField
from sdg.api.serializers.organisaties import (
    BevoegdeOrganisatieSerializer,
    LocatieBaseSerializer,
    OpeningstijdenSerializer,
)
from sdg.core.constants.product import TaalChoices
from sdg.core.models.catalogus import ProductenCatalogus
from sdg.organisaties.models import (
    BevoegdeOrganisatie,
    LokaleOverheid,
    Lokatie as Locatie,
)
from sdg.producten.models import LocalizedProduct, Product, ProductVersie
from sdg.producten.models.product import GeneriekProduct


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
            "product_aanwezig_toelichting",
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

    upn_label = serializers.CharField(
        source="generiek_product.upn_label",
        required=False,
    )
    upn_uri = serializers.URLField(
        source="generiek_product.upn_uri",
        required=False,
    )

    class Meta:
        model = Product
        fields = ("url", "upn_uri", "upn_label")
        extra_kwargs = {
            "url": {
                "view_name": "api:product-detail",
                "lookup_field": "uuid",
            }
        }


class ProductLocatieSerializer(LocatieBaseSerializer):
    openingstijden = OpeningstijdenSerializer(read_only=True)

    class Meta(LocatieBaseSerializer.Meta):
        read_only_fields = (
            "url",
            "straat",
            "nummer",
            "postcode",
            "plaats",
            "land",
            "openingstijden_opmerking",
        )
        fields = (
            "openingstijden",
            "uuid",
            "naam",
        )

        extra_kwargs = {
            "naam": {
                "required": False,
            },
            "uuid": {
                "required": False,
                "read_only": False,
            },
        }


class ProductLokaleOverheidSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer that exposes a small subset of the fields for an organization, used in references to an organization.
    - Fields: `url`, `owmsIdentifier`, `owmsPrefLabel`
    """

    owms_identifier = serializers.URLField(
        source="catalogi.organisatie.owms_identifier",
        help_text="OWMS identifier van de hoofdorganisatie van deze lokale overheid.",
        required=False,
    )
    owms_pref_label = serializers.CharField(
        source="catalogi.organisatie.owms_pref_label",
        help_text="OWMS label van de hoofdorganisatie van deze lokale overheid.",
        required=False,
    )
    owms_end_date = serializers.DateTimeField(
        source="catalogi.organisatie.owms_end_date",
        help_text="De einddatum, zoals gevonden in het OWMS-model.",
        read_only=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = (
            "url",
            "owms_identifier",
            "owms_pref_label",
            "owms_end_date",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:lokaleoverheid-detail",
                "lookup_field": "uuid",
            },
        }

    def to_representation(self, instance):
        data = super(ProductLokaleOverheidSerializer, self).to_representation(instance)

        data.update(
            url=reverse(
                "api:lokaleoverheid-detail",
                [str(instance.catalogus.lokale_overheid.uuid)],
            ),
            owms_pref_label=instance.catalogus.lokale_overheid.organisatie.owms_pref_label,
            owms_identifier=instance.catalogus.lokale_overheid.organisatie.owms_identifier,
            owms_end_date=instance.catalogus.lokale_overheid.organisatie.owms_end_date,
        )

        return data


class ProductSerializer(ProductBaseSerializer):
    """Serializer for a product, including UPN, availability, locations and latest version translations."""

    verantwoordelijke_organisatie = ProductLokaleOverheidSerializer(
        source="*",
    )
    publicatie_datum = serializers.DateField(
        source="most_recent_version.publicatie_datum",
        allow_null=True,
    )
    product_aanwezig = serializers.BooleanField(allow_null=True, required=True)
    vertalingen = LocalizedProductSerializer(
        source="most_recent_version.vertalingen", many=True
    )
    versie = SerializerMethodField(method_name="get_versie")
    doelgroep = SerializerMethodField(method_name="get_doelgroep")
    gerelateerde_producten = ProductBaseSerializer(many=True)
    locaties = ProductLocatieSerializer(
        allow_null=True,
        many=True,
    )
    bevoegde_organisatie = BevoegdeOrganisatieSerializer(
        required=False, allow_null=True
    )
    product_valt_onder = ProductBaseSerializer(allow_null=True, required=True)

    class Meta:
        model = Product
        fields = (
            "url",
            "uuid",
            "upn_label",
            "upn_uri",
            "versie",
            "publicatie_datum",
            "product_aanwezig",
            "product_valt_onder",
            "verantwoordelijke_organisatie",
            "bevoegde_organisatie",
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
                "required": False,
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
    def _get_most_recent_version(product: Product, field_name, default=None):
        """Get the value of a field from the product's active version."""
        most_recent_version = getattr(product, "most_recent_version", None)
        return (
            getattr(most_recent_version, field_name) if most_recent_version else default
        )

    def get_vertalingen(self, obj: Product):
        return LocalizedProduct.objects.filter(
            product_versie=getattr(obj, "most_recent_version", None)
        )

    def get_versie(self, obj: Product) -> int:
        return self._get_most_recent_version(obj, "versie", default=0)

    def get_doelgroep(self, obj: Product) -> str:
        return obj.generiek_product.doelgroep

    def to_representation(self, instance):
        data = super(ProductBaseSerializer, self).to_representation(instance)
        translations = self.get_vertalingen(instance)

        if translations and getattr(instance, "_filter_taal", None):
            filtered_translations = [
                i for i in translations if i.taal == instance._filter_taal
            ]

            data.update(
                vertalingen=LocalizedProductSerializer(
                    filtered_translations, many=True
                ).data
            )

        return data

    def validate(self, attrs):
        if "generiek_product" not in attrs:
            raise serializers.ValidationError("You forgot to provide a product")

        most_recent_version = attrs["most_recent_version"]

        required_taalen = [taal[0] for taal in TaalChoices]
        for version in most_recent_version["vertalingen"]:
            if version["taal"] in required_taalen:
                required_taalen.remove(version["taal"])

        if required_taalen:
            raise serializers.ValidationError(
                f"You forgot to provide the taal choice(s): {required_taalen}"
            )

        if most_recent_version["vertalingen"]:
            if not attrs["product_aanwezig"]:
                for vertaling in most_recent_version["vertalingen"]:
                    if (
                        not vertaling["product_aanwezig_toelichting"]
                        or vertaling["product_aanwezig_toelichting"] == ""
                    ):
                        raise serializers.ValidationError(
                            "You forgot to provide the product_aanwezig_toelichting"
                        )

            if attrs["product_valt_onder"]:
                for vertaling in most_recent_version["vertalingen"]:
                    if (
                        not vertaling["product_valt_onder_toelichting"]
                        or vertaling["product_valt_onder_toelichting"] == ""
                    ):
                        raise serializers.ValidationError(
                            "You forgot to provide the product_valt_onder_toelichting"
                        )

        return attrs

    def get_generiek_product(self, generiek_product):
        if "upn_label" in generiek_product:
            try:
                return GeneriekProduct.objects.get(
                    upn__upn_label=generiek_product["upn_label"]
                )
            except GeneriekProduct.DoesNotExist:
                raise serializers.ValidationError("Received a non existing 'upn label'")

        if "upn_uri" in generiek_product:
            try:
                return GeneriekProduct.objects.get(
                    upn__upn_uri=generiek_product["upn_uri"]
                )
            except GeneriekProduct.DoesNotExist:
                raise serializers.ValidationError("Received a non existing 'upn uri'")

    def get_default_catalogus(self, verantwoordelijke_organisatie):
        try:
            return ProductenCatalogus.objects.get(
                lokale_overheid=verantwoordelijke_organisatie,
                is_default_catalogus=True,
            )
        except ProductenCatalogus.DoesNotExist:
            raise serializers.ValidationError("Could not find a default catalog.")

    def get_referentie_product(self, generiek_product):
        referentie_product = Product.objects.get(
            generiek_product=generiek_product,
            referentie_product=None,
        )

        return referentie_product

    def get_product(self, product_valt_onder, catalogus):
        if "upn_label" in product_valt_onder:
            try:
                return Product.objects.get(
                    generiek_product__upn__upn_label=product_valt_onder["upn_label"],
                    catalogus=catalogus,
                )
            except Product.DoesNotExist:
                raise serializers.ValidationError("Received a non existing 'upn label'")

        if "upn_uri" in product_valt_onder:
            try:
                return Product.objects.get(
                    generiek_product__upn__upn_uri=product_valt_onder["upn_uri"],
                    catalogus=catalogus,
                )
            except Product.DoesNotExist:
                raise serializers.ValidationError("Received a non existing 'upn uri'")

    def get_lokale_overheid(self, organisatie):
        if "owms_pref_label" in organisatie and organisatie["owms_pref_label"]:
            try:
                return LokaleOverheid.objects.get(
                    organisatie__owms_pref_label=organisatie["owms_pref_label"]
                )
            except LokaleOverheid.DoesNotExist:
                raise serializers.ValidationError(
                    "Received a non existing 'owms pref label'"
                )

        if "owms_identifier" in organisatie and organisatie["owms_identifier"]:
            try:
                return LokaleOverheid.objects.get(
                    organisatie__owms_identifier=organisatie["owms_identifier"]
                )
            except LokaleOverheid.DoesNotExist:
                raise serializers.ValidationError(
                    "Received a non existing 'owms identifier'"
                )

    def get_bevoegde_organisatie(self, organisatie):
        if "naam" in organisatie and organisatie["naam"]:
            try:
                return BevoegdeOrganisatie.objects.get(naam=organisatie["naam"])
            except BevoegdeOrganisatie.DoesNotExist:
                raise serializers.ValidationError("Received a non existing 'naam'")

        if (
            "owms_pref_label" in organisatie["organisatie"]
            and organisatie["organisatie"]["owms_pref_label"]
        ):
            try:
                return BevoegdeOrganisatie.objects.get(
                    lokale_overheid__organisatie__owms_pref_label=organisatie[
                        "organisatie"
                    ]["owms_pref_label"]
                )
            except BevoegdeOrganisatie.DoesNotExist:
                raise serializers.ValidationError(
                    "Received a non existing 'owms pref label'"
                )

        if (
            "owms_identifier" in organisatie["organisatie"]
            and organisatie["organisatie"]["owms_identifier"]
        ):
            try:
                return BevoegdeOrganisatie.objects.get(
                    lokale_overheid__organisatie__owms_identifier=organisatie[
                        "organisatie"
                    ]["owms_identifier"]
                )
            except BevoegdeOrganisatie.DoesNotExist:
                raise serializers.ValidationError(
                    "Received a non existing 'owms identifier'"
                )

    def get_locaties(self, locaties, catalogus):
        organisatie_locaties = []
        for locatie in locaties:
            if "uuid" in locatie:
                try:
                    organisatie_locaties.append(
                        Locatie.objects.get(
                            uuid=locatie["uuid"],
                            lokale_overheid__organisatie=catalogus.lokale_overheid.organisatie,
                        )
                    )
                except Locatie.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Received a non existing 'locatie' of catalogus {catalogus}"
                    )
            elif "naam" in locatie:
                # TODO change to get when unique is in place

                overheid_locatie = Locatie.objects.filter(
                    naam=locatie["naam"],
                    lokale_overheid__organisatie=catalogus.lokale_overheid.organisatie,
                ).first()

                if not overheid_locatie:
                    raise serializers.ValidationError(
                        f"Received a non existing 'locatie' of catalogus {catalogus}"
                    )

                organisatie_locaties.append(overheid_locatie)

        return organisatie_locaties

    @transaction.atomic
    def create(self, validated_data):
        data = self.context["request"].data.copy()
        generiek_product = validated_data.pop("generiek_product")
        catalogus = validated_data.get("catalogus", [])
        product_valt_onder = validated_data.pop("product_valt_onder", [])
        gerelateerde_producten = validated_data.pop("gerelateerde_producten", [])
        verantwoordelijke_organisatie = data.get("verantwoordelijke_organisatie", [])
        bevoegde_organisatie = validated_data.pop("bevoegde_organisatie", [])
        locaties = validated_data.pop("locaties", [])

        most_recent_version = validated_data.pop("most_recent_version")
        publicatie_datum = most_recent_version.pop("publicatie_datum", None)
        vertalingen = most_recent_version.pop("vertalingen", [])

        validated_data["generiek_product"] = self.get_generiek_product(generiek_product)

        if verantwoordelijke_organisatie:
            verantwoordelijke_organisatie = self.get_lokale_overheid(
                verantwoordelijke_organisatie
            )

        if not catalogus:
            validated_data["catalogus"] = self.get_default_catalogus(
                verantwoordelijke_organisatie
            )

        if not validated_data.get("catalogus").is_referentie_catalogus:
            validated_data["referentie_product"] = self.get_referentie_product(
                validated_data["generiek_product"]
            )
        else:
            raise serializers.ValidationError("Received a referentie catalogus")

        if product_valt_onder:
            if "generiek_product" in product_valt_onder:
                validated_data["product_valt_onder"] = self.get_product(
                    product_valt_onder["generiek_product"],
                    validated_data["catalogus"],
                )

        if bevoegde_organisatie:
            if "organisatie" in bevoegde_organisatie:
                validated_data["bevoegde_organisatie"] = self.get_bevoegde_organisatie(
                    bevoegde_organisatie
                )
        else:
            validated_data["bevoegde_organisatie"] = BevoegdeOrganisatie.objects.get(
                lokale_overheid=verantwoordelijke_organisatie
            )

        product = Product.objects.get(
            referentie_product=validated_data["referentie_product"],
            catalogus=validated_data["catalogus"],
        )

        product.product_valt_onder = validated_data.get("product_valt_onder", None)
        product.product_aanwezig = validated_data.get("product_aanwezig", None)
        product.bevoegde_organisatie = validated_data.get("bevoegde_organisatie", None)

        product.save()

        product.locaties.set(
            self.get_locaties(
                locaties,
                validated_data["catalogus"],
            )
        )

        if gerelateerde_producten:
            gerelateerde_catalogus_producten = []
            for gerelateerde_product in gerelateerde_producten:
                if "generiek_product" in gerelateerde_product:
                    gerelateerde_catalogus_producten.append(
                        self.get_product(
                            gerelateerde_product["generiek_product"],
                            validated_data["catalogus"],
                        )
                    )
            product.gerelateerde_producten.set(gerelateerde_catalogus_producten)

        versie = product.most_recent_version.versie

        if product.most_recent_version.publicatie_datum:
            versie += 1

        product_versie, product_versie_created = ProductVersie.objects.update_or_create(
            product=product,
            versie=versie,
            publicatie_datum=None,
            defaults={"publicatie_datum": publicatie_datum},
        )

        if vertalingen:
            for vertaling in vertalingen:

                if product_versie_created:

                    LocalizedProduct.objects.create(
                        **vertaling,
                        product_versie=product_versie,
                    )

                else:
                    vertaling["product_versie"] = product_versie

                    LocalizedProduct.objects.filter(
                        taal=vertaling["taal"], product_versie=product_versie
                    ).update(**vertaling)

        return product
