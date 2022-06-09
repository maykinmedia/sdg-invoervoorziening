from datetime import date

from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from sdg.api.serializers.fields import LabeledUrlListField
from sdg.api.serializers.organisaties import (
    BevoegdeOrganisatieSerializer,
    LocatieBaseSerializer,
    LokaleOverheidBaseSerializer,
    OpeningstijdenSerializer,
)
from sdg.core.models import catalogus
from sdg.organisaties.models import BevoegdeOrganisatie, Lokatie as Locatie
from sdg.organisaties.urls import catalog
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


class LocatieSerializer(LocatieBaseSerializer):
    url = serializers.CharField(read_only=True)
    uuid = serializers.CharField()
    naam = serializers.CharField()
    straat = serializers.CharField(read_only=True)
    nummer = serializers.CharField(read_only=True)
    postcode = serializers.CharField(read_only=True)
    plaats = serializers.CharField(read_only=True)
    land = serializers.CharField(read_only=True)
    openingstijden_opmerking = serializers.CharField(read_only=True)
    openingstijden = OpeningstijdenSerializer(read_only=True, source="*")

    class Meta:
        model = Locatie
        fields = (
            "url",
            "uuid",
            "naam",
            "straat",
            "nummer",
            "postcode",
            "plaats",
            "land",
            "openingstijden_opmerking",
            "openingstijden",
        )


class ProductSerializer(ProductBaseSerializer):
    """Serializer for a product, including UPN, availability, locations and latest version translations."""

    verantwoordelijke_organisatie = LokaleOverheidBaseSerializer(
        source="catalogus.lokale_overheid",
    )
    publicatie_datum = SerializerMethodField(method_name="get_publicatie_datum")
    vertalingen = SerializerMethodField(method_name="get_vertalingen")
    versie = SerializerMethodField(method_name="get_versie")
    doelgroep = SerializerMethodField(method_name="get_doelgroep")
    gerelateerde_producten = ProductBaseSerializer(many=True)
    locaties = LocatieSerializer(many=True)
    bevoegde_organisatie = BevoegdeOrganisatieSerializer(required=False)
    product_valt_onder = ProductBaseSerializer(allow_null=True)

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
                "allow_null": True,
                "default": "",
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
        return obj.generiek_product.doelgroep

    def does_product_exist(self, generiek_product, catalogus):
        product_exists = Product.objects.filter(
            generiek_product=generiek_product,
            catalogus=catalogus,
        ).exists()

        if product_exists:
            raise serializers.ValidationError(
                f"Product '{generiek_product}' already exists for catalogus '{catalogus}'"
            )

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
            return catalogus.ProductenCatalogus.objects.get(
                lokale_overheid=verantwoordelijke_organisatie.lokale_overheid,
                is_default_catalogus=True,
            )
        except catalogus.ProductenCatalogus.DoesNotExist:
            raise serializers.ValidationError("Didn't receive a catalogus")

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

    def get_organisatie(self, organisatie):
        if "owms_pref_label" in organisatie:
            try:
                return BevoegdeOrganisatie.objects.get(
                    lokale_overheid__organisatie__owms_pref_label=organisatie[
                        "owms_pref_label"
                    ]
                )
            except BevoegdeOrganisatie.DoesNotExist:
                raise serializers.ValidationError(
                    "Received a non existing 'owms pref label'"
                )

        if "owms_identifier" in organisatie:
            try:
                return BevoegdeOrganisatie.objects.get(
                    lokale_overheid__organisatie__owms_identifier=organisatie[
                        "owms_identifier"
                    ]
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
                            lokale_overheid__organisatie__owms_pref_label=catalogus.lokale_overheid.organisatie.owms_pref_label,
                        )
                    )
                except Locatie.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Received a non existing 'locatie' of catalogus {catalogus}"
                    )
            elif "naam" in locatie:
                # TODO change to get when unique is in place
                try:
                    organisatie_locaties.append(
                        Locatie.objects.filter(
                            naam=locatie["naam"],
                            lokale_overheid__organisatie__owms_pref_label=catalogus.lokale_overheid.organisatie.owms_pref_label,
                        ).first()
                    )
                except Locatie.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Received a non existing 'locatie' of catalogus {catalogus}"
                    )

        return organisatie_locaties

    @transaction.atomic
    def create(self, validated_data):
        data = self.context["request"].data.copy()
        generiek_product = validated_data.pop("generiek_product")
        product_valt_onder = validated_data.pop("product_valt_onder", [])
        gerelateerde_producten = validated_data.pop("gerelateerde_producten", [])
        verantwoordelijke_organisatie = data.get("verantwoordelijke_organisatie", [])
        bevoegde_organisatie = validated_data.pop("bevoegde_organisatie", [])
        locaties = validated_data.pop("locaties", [])

        validated_data["generiek_product"] = self.get_generiek_product(generiek_product)

        if verantwoordelijke_organisatie:
            verantwoordelijke_organisatie = self.get_organisatie(
                verantwoordelijke_organisatie
            )

        if not validated_data["catalogus"]:
            validated_data["catalogus"] = self.get_default_catalogus(
                verantwoordelijke_organisatie
            )

        self.does_product_exist(
            generiek_product=validated_data["generiek_product"],
            catalogus=validated_data["catalogus"],
        )

        if not validated_data["catalogus"].is_referentie_catalogus:
            validated_data["referentie_product"] = self.get_referentie_product(
                validated_data["generiek_product"]
            )

        if product_valt_onder:
            if "generiek_product" in product_valt_onder:
                validated_data["product_valt_onder"] = self.get_product(
                    product_valt_onder["generiek_product"],
                    validated_data["catalogus"],
                )

        if bevoegde_organisatie:
            if "organisatie" in bevoegde_organisatie:
                validated_data["bevoegde_organisatie"] = self.get_organisatie(
                    bevoegde_organisatie["organisatie"]
                )
        else:
            validated_data["bevoegde_organisatie"] = verantwoordelijke_organisatie

        product = Product.objects.create(**validated_data)

        if locaties:
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

        publicatie_datum = data.get("publicatie_datum", "")

        product_versie = ProductVersie.objects.create(
            product=product,
            versie=1,
            publicatie_datum=publicatie_datum,
        )

        vertalingen = data.get("vertalingen", [])

        if vertalingen:
            for vertaling in vertalingen:
                vertaling["product_versie"] = product_versie
                for field, value in vertaling.items():
                    if value is None:
                        message = f"Het veld '{field}' van de taal '{vertaling['taal']}' mag niet leeg zijn."
                        raise serializers.ValidationError(message)

                LocalizedProduct.objects.create(**vertaling)

        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        data = self.context["request"].data.copy()
        generiek_product = instance.generiek_product
        product_valt_onder = validated_data.pop("product_valt_onder", [])
        gerelateerde_producten = validated_data.pop("gerelateerde_producten", [])
        verantwoordelijke_organisatie = data.get("verantwoordelijke_organisatie", [])
        bevoegde_organisatie = validated_data.pop("bevoegde_organisatie", [])
        locaties = validated_data.pop("locaties", [])

        if verantwoordelijke_organisatie:
            verantwoordelijke_organisatie = self.get_organisatie(
                verantwoordelijke_organisatie
            )

        if not validated_data["catalogus"]:
            validated_data["catalogus"] = self.get_default_catalogus(
                verantwoordelijke_organisatie
            )

        if not validated_data["catalogus"].is_referentie_catalogus:
            validated_data["referentie_product"] = self.get_referentie_product(
                generiek_product
            )

        if product_valt_onder:
            if "generiek_product" in product_valt_onder:
                validated_data["product_valt_onder"] = self.get_product(
                    product_valt_onder["generiek_product"],
                    validated_data["catalogus"],
                )

        if bevoegde_organisatie:
            if "organisatie" in bevoegde_organisatie:
                validated_data["bevoegde_organisatie"] = self.get_organisatie(
                    bevoegde_organisatie["organisatie"]
                )
        else:
            validated_data["bevoegde_organisatie"] = verantwoordelijke_organisatie

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
            validated_data["gerelateerde_producten"] = gerelateerde_catalogus_producten

        if locaties:
            validated_data["locaties"] = self.get_locaties(
                locaties,
                validated_data["catalogus"],
            )

        instance.catalogus = validated_data.get("catalogus", instance.catalogus)
        instance.generiek_product = validated_data.get(
            "generiek_product", instance.generiek_product
        )
        instance.referentie_product = validated_data.get(
            "referentie_product", instance.referentie_product
        )
        instance.gerelateerde_producten.set(
            validated_data.get(
                "gerelateerde_producten", instance.gerelateerde_producten
            )
        )
        instance.product_aanwezig = validated_data.get(
            "product_aanwezig", instance.product_aanwezig
        )
        instance.product_valt_onder = validated_data.get(
            "product_valt_onder", instance.product_valt_onder
        )
        instance.locaties.set(validated_data.get("locaties", instance.locaties))

        product_versie = ProductVersie.objects.filter(product=instance).first()

        publicatie_datum = data.get("publicatie_datum", "")
        vertalingen = data.get("vertalingen", [])

        if product_versie.publicatie_datum:
            product_versie = ProductVersie.objects.create(
                product=instance,
                versie=product_versie.versie + 1,
                publicatie_datum=publicatie_datum,
            )

            if vertalingen:
                for vertaling in vertalingen:
                    vertaling["product_versie"] = product_versie
                    for field, value in vertaling.items():
                        if value is None:
                            message = f"Het veld '{field}' van de taal '{vertaling['taal']}' mag niet leeg zijn."
                            raise serializers.ValidationError(message)

                    LocalizedProduct.objects.create(**vertaling)
        else:
            product_versie.publicatie_datum = publicatie_datum
            product_versie.save()

            if vertalingen:
                for vertaling in vertalingen:
                    vertaling["product_versie"] = product_versie
                    for field, value in vertaling.items():
                        if value is None:
                            message = f"Het veld '{field}' van de taal '{vertaling['taal']}' mag niet leeg zijn."
                            raise serializers.ValidationError(message)

                    localized_product = LocalizedProduct.objects.get(
                        taal=vertaling["taal"], product_versie=product_versie
                    )
                    super().update(localized_product, vertaling)

        return instance
