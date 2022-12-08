import datetime

from django.db import transaction
from django.utils.dateparse import parse_date

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.reverse import reverse

from sdg.api.serializers.fields import LabeledUrlListField
from sdg.api.serializers.organisaties import (
    BevoegdeOrganisatieSerializer,
    LocatieBaseSerializer,
    OpeningstijdenSerializer,
)
from sdg.core.constants.product import DoelgroepChoices, TaalChoices
from sdg.core.models.catalogus import ProductenCatalogus
from sdg.organisaties.models import (
    BevoegdeOrganisatie,
    LokaleOverheid,
    Lokatie as Locatie,
)
from sdg.producten.models import LocalizedProduct, Product, ProductVersie
from sdg.producten.models.product import GeneriekProduct


class ProcedureLink(serializers.ModelSerializer):
    class Meta:
        model = LocalizedProduct
        fields = (
            "label",
            "url",
        )
        extra_kwargs = {
            "label": {
                "source": "decentrale_procedure_label",
                "help_text": "Het label waarmee de URL wordt aangeduid.",
            },
            "url": {
                "source": "decentrale_procedure_link",
                "help_text": "De URL waar de burger of ondernemer het product bij de organisatie kan aanvragen.",
            },
        }


class LocalizedProductSerializer(serializers.ModelSerializer):
    """Serializer for the localized version of a product."""

    links = LabeledUrlListField(
        source="verwijzing_links",
        help_text="Dit zijn de verwijzing links voor burgers en ondernemers naar relevante organisatie informatie.",
        required=False,
    )
    procedure_link = ProcedureLink(
        source="*", required=False, help_text="Het label en de link naar de procedure."
    )

    class Meta:
        model = LocalizedProduct
        fields = (
            "taal",
            "titel",
            "tekst",
            "links",
            "procedure_beschrijving",
            "bewijs",
            "vereisten",
            "bezwaar_en_beroep",
            "kosten_en_betaalmethoden",
            "uiterste_termijn",
            "wtd_bij_geen_reactie",
            "procedure_link",
            "product_aanwezig_toelichting",
            "product_valt_onder_toelichting",
            "datum_wijziging",
        )
        extra_kwargs = {
            "taal": {
                "help_text": """De taal van de onderstaande gegevens volgens formaat [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)."""
            },
            "titel": {
                "source": "product_titel_decentraal",
                "help_text": "De titel van het product. Als deze afwijkt van de generieke titel kunt u dat hier aangeven.",
            },
            "tekst": {
                "source": "specifieke_tekst",
                "help_text": "De inleidende tekst voor het product. Hierin kunt u het product beschrijven en komt direct na de generieke productbeschrijving. Dit veld ondersteund Markdown.",
            },
            "procedure_beschrijving": {
                "help_text": "De beschrijving van hoe het product wordt aangevraagd. Dit veld ondersteund Markdown."
            },
            "bewijs": {
                "help_text": "Dit bevat de bewijsstukken die de burger of ondernemer nodig heeft om dit product aan te vragen. Dit veld ondersteund Markdown."
            },
            "vereisten": {
                "help_text": "Dit zijn de voorwaarden voor het aanvragen van het product. Dit veld ondersteund Markdown."
            },
            "bezwaar_en_beroep": {
                "help_text": "Beschrijft hoe de burger of ondernemer bezwaar kan maken. Dit veld ondersteund Markdown."
            },
            "kosten_en_betaalmethoden": {
                "help_text": "Beschrijft hoe de burger of ondernemer kan betalen en wat de kosten zijn. Dit veld ondersteund Markdown."
            },
            "uiterste_termijn": {
                "help_text": "De informatie over hoe hoelang het duurt voor het aanvragen van dit product. Dit doet u aan de hand van werkdagen/weken. Dit veld ondersteund Markdown."
            },
            "wtd_bij_geen_reactie": {
                "help_text": "Beschrijft wat de aanvrager moet doen bij geen reactie. Dit veld ondersteund Markdown."
            },
            "product_aanwezig_toelichting": {
                "help_text": "Een optioneel veld om uit te leggen waarom het product niet aanwezig is. Deze moet u alleen invullen als u het product niet levert en dan is dit veld verplicht! Dit veld ondersteund Markdown."
            },
            "product_valt_onder_toelichting": {
                "help_text": "Een optioneel veld om uit te leggen waarom dit product onder een andere product valt. Deze moet u alleen invullen als dit product onder een andere product valt en dan is dit veld verplicht! Dit veld ondersteund Markdown."
            },
            "datum_wijziging": {
                "help_text": "Datum wanneer dit product voor het laatst is gewijzigd."
            },
        }


class ProductVersieSerializer(serializers.ModelSerializer):
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
    upn_label = serializers.CharField(
        source="generiek_product.upn_label",
        required=False,
        help_text="Het UPN Label van het specifieke product.",
    )
    upn_uri = serializers.URLField(
        source="generiek_product.upn_uri",
        required=True,
        help_text="De UPN URI van het specifieke product.",
    )

    class Meta:
        model = Product
        fields = ("url", "upn_uri", "upn_label")
        extra_kwargs = {
            "url": {
                "view_name": "api:product-detail",
                "lookup_field": "uuid",
                "help_text": "De unieke URL van dit object binnen deze API.",
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
            "url",
            "naam",
        )

        extra_kwargs = {
            "naam": {
                "required": False,
            },
            "url": {
                "view_name": "api:locatie-detail",
                "lookup_field": "uuid",
                "help_text": "De unieke URL van dit object binnen deze API.",
            },
        }


class ProductLokaleOverheidSerializer(serializers.HyperlinkedModelSerializer):
    """De organisatie die dit product levert en de teksten hiervan beheert."""

    url = serializers.SerializerMethodField(
        help_text="De unieke URL van dit object binnen deze API."
    )
    owms_identifier = serializers.URLField(
        source="catalogus.lokale_overheid.organisatie.owms_identifier",
        help_text="De OWMS Identifier van de hoofdorganisatie van deze lokale overheid.",
        required=True,
    )
    owms_pref_label = serializers.CharField(
        source="catalogus.lokale_overheid.organisatie.owms_pref_label",
        help_text="OWMS label van de hoofdorganisatie van deze lokale overheid.",
        required=False,
    )
    owms_end_date = serializers.DateTimeField(
        source="catalogus.lokale_overheid.organisatie.owms_end_date",
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

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, instance):
        return reverse(
            "api:lokaleoverheid-detail",
            [str(instance.catalogus.lokale_overheid.uuid)],
            request=self.context["request"],
        )


class ProductSerializer(ProductBaseSerializer):
    """Serializer for a product, including UPN, availability, locations and latest version translations."""

    verantwoordelijke_organisatie = ProductLokaleOverheidSerializer(source="*")
    publicatie_datum = serializers.DateField(
        source="most_recent_version.publicatie_datum",
        allow_null=True,
        help_text="De datum die aangeeft wanneer het product gepubliceerd is/wordt.",
    )
    product_aanwezig = serializers.BooleanField(
        allow_null=True,
        required=True,
        help_text="Een boolean die aangeeft of de organisatie dit product levert of niet. Als de verantwoordelijke organisatie niet expliciet heeft aangegeven dat een product aanwezig of afwezig is, dan is deze waarde `null`. Als een product afwezig is, dan moet er een toelichting worden gegeven in alle beschikbare talen. Alle andere vertaalde velden kunnen dan leeg blijven.",
    )
    vertalingen = LocalizedProductSerializer(
        source="most_recent_version.vertalingen",
        many=True,
        help_text="Een lijst met specifieke teksten op basis van taal.",
    )
    beschikbare_talen = serializers.SerializerMethodField(
        method_name="get_talen",
        help_text="Alle beschikbare talen.",
    )
    versie = SerializerMethodField(
        method_name="get_versie", help_text="De huidige versie van dit product."
    )
    doelgroep = serializers.ChoiceField(
        source="generiek_product.doelgroep",
        choices=DoelgroepChoices.choices,
        required=True,
        help_text="De doelgroep van dit product.",
    )
    locaties = ProductLocatieSerializer(
        allow_null=True,
        many=True,
        help_text="Een lijst met locaties waarop dit product beschikbaar is.",
    )
    bevoegde_organisatie = BevoegdeOrganisatieSerializer(
        required=False,
        allow_null=True,
        help_text="De bevoegde organisatie van dit product is (als die er niet is wordt de verantwoordelijke organisatie standaard de bevoegde organisatie.)",
    )
    product_valt_onder = ProductBaseSerializer(
        allow_null=True,
        required=True,
        help_text="Als een product valt onder een ander product (het product wordt bijvoorbeeld geleverd middels een ander product), dan staat deze hier vermeld. Als een product onder een ander product valt, dan moet er een toelichting worden gegeven in alle beschikbare talen. Alle andere vertaalde velden kunnen dan leeg blijven.",
    )

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
            "beschikbare_talen",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:product-detail",
                "lookup_field": "uuid",
                "help_text": "De unieke URL van dit object binnen deze API.",
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

    def get_talen(self, obj: Product) -> list:
        return TaalChoices.get_available_languages()

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
            raise serializers.ValidationError(
                {"generiekProduct": "Het veld 'product' is verplicht."}
            )

        most_recent_version = attrs["most_recent_version"]

        required_taalen = [taal[0] for taal in TaalChoices]
        for version in most_recent_version["vertalingen"]:
            if version["taal"] in required_taalen:
                required_taalen.remove(version["taal"])

        if required_taalen:
            raise serializers.ValidationError(
                {
                    "vertalingen": f"Het veld 'taal' is verplicht. Geldige waarden zijn: {required_taalen}"
                }
            )

        if most_recent_version["vertalingen"]:
            if not attrs["product_aanwezig"]:
                for vertaling in most_recent_version["vertalingen"]:
                    if (
                        not vertaling["product_aanwezig_toelichting"]
                        or vertaling["product_aanwezig_toelichting"] == ""
                    ):
                        raise serializers.ValidationError(
                            {
                                "productAanwezigToelichting": "Het veld 'productAanwezigToelichting' is verplicht als het product niet aanwezig is."
                            }
                        )

            if attrs["product_valt_onder"]:
                for vertaling in most_recent_version["vertalingen"]:
                    if (
                        not vertaling["product_valt_onder_toelichting"]
                        or vertaling["product_valt_onder_toelichting"] == ""
                    ):
                        raise serializers.ValidationError(
                            {
                                "productValtOnderToelichting": "Het veld 'productValtOnderToelichting' is verplicht als het product onder een ander product valt."
                            }
                        )

        return attrs

    def get_generiek_product(self, generiek_product, doelgroep):
        if "upn_uri" in generiek_product:
            try:
                return GeneriekProduct.objects.get(
                    upn__upn_uri=generiek_product["upn_uri"], doelgroep=doelgroep
                )
            except GeneriekProduct.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "upnUri": "De waarde van het veld 'upnUri' is ongeldig. Het object met deze waarde bestaat niet."
                    }
                )
            except KeyError:
                raise serializers.ValidationError(
                    {"upnUri": "Het veld 'upnUri' is verplicht.'"}
                )

    def get_default_catalogus(self, verantwoordelijke_organisatie):
        try:
            return ProductenCatalogus.objects.get(
                lokale_overheid=verantwoordelijke_organisatie,
                is_default_catalogus=True,
            )
        except ProductenCatalogus.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "": "Het veld 'catalogus' is verplicht omdat er geen standaard catalogus beschikbaar is."
                }
            )

    def get_referentie_product(self, generiek_product):
        try:
            referentie_product = Product.objects.get(
                generiek_product=generiek_product,
                referentie_product=None,
            )

            return referentie_product
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "upnUri": "Het product is niet (meer) gekoppeld aan een referentie product."
                }
            )

    def get_product(self, product_valt_onder, catalogus):
        try:
            return Product.objects.get(
                generiek_product__upn__upn_uri=product_valt_onder["upn_uri"],
                catalogus=catalogus,
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "upnUri": "De waarde van het veld 'upnUri' is ongeldig. Het object met deze waarde bestaat niet."
                }
            )
        except KeyError:
            raise serializers.ValidationError(
                {"upnUri": "Het veld 'upnUri' is verplicht."}
            )

    def get_lokale_overheid(self, organisatie):
        try:
            return LokaleOverheid.objects.get(
                organisatie__owms_identifier=organisatie["owms_identifier"]
            )
        except LokaleOverheid.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "owmsIdentifier": "De waarde van het veld 'owmsIdentifier' is ongeldig. Het object met deze waarde bestaat niet."
                }
            )
        except KeyError:
            raise serializers.ValidationError(
                {"owmsIdentifier": "Het veld 'owmsIdentifier' is verplicht."}
            )

    def get_bevoegde_organisatie(self, organisatie, verantwoordelijke_organisatie):
        if "naam" in organisatie and organisatie["naam"]:
            try:
                return BevoegdeOrganisatie.objects.get(
                    naam=organisatie["naam"],
                    lokale_overheid=verantwoordelijke_organisatie,
                )
            except BevoegdeOrganisatie.DoesNotExist:

                raise serializers.ValidationError(
                    {
                        "verantwoordelijkeOrganisatie.naam": "De waarde van het veld 'naam' is ongeldig. Het object met deze waarde bestaat niet."
                    }
                )

        if (
            "owms_identifier" in organisatie["organisatie"]
            and organisatie["organisatie"]["owms_identifier"]
        ):
            try:
                return BevoegdeOrganisatie.objects.get(
                    organisatie__owms_identifier=organisatie["organisatie"][
                        "owms_identifier"
                    ],
                    lokale_overheid=verantwoordelijke_organisatie,
                )
            except BevoegdeOrganisatie.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "verantwoordelijkeOrganisatie.owmsIdentifier": "De waarde van het veld 'owmsIdentifier' is ongeldig. Het object met deze waarde bestaat niet."
                    }
                )

        return None

    def get_version_number(self, previous_date, new_date, version):
        if not previous_date:
            return version

        if not new_date and previous_date <= datetime.date.today():
            return version + 1

        if not new_date:
            return version

        if new_date < previous_date and new_date < datetime.date.today():
            raise serializers.ValidationError(
                {
                    "publicatieDatum": "Het product kan niet een vroegere publicatiedatum krijgen dan een voorgaande versie."
                }
            )

        if new_date <= datetime.date.today():
            return version + 1

        if previous_date > datetime.date.today() and new_date > datetime.date.today():
            return version

        if previous_date < new_date and new_date > datetime.date.today():
            return version + 1

        return version

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
                        f"De 'locatie' die u meegegeven heeft bestaat niet in de catalogus: {catalogus.lokale_overheid.organisatie}."
                    )
            if "naam" in locatie:
                overheid_locatie = Locatie.objects.get(
                    naam=locatie["naam"],
                    lokale_overheid__organisatie=catalogus.lokale_overheid.organisatie,
                )

                if not overheid_locatie:
                    raise serializers.ValidationError(
                        {
                            "locaties.naam": f"De 'locatie' die u meegegeven heeft bestaat niet in de catalogus: {catalogus.lokale_overheid.organisatie}."
                        }
                    )

                organisatie_locaties.append(overheid_locatie)

        return organisatie_locaties

    @transaction.atomic
    def create(self, validated_data):
        data = self.context["request"].data.copy()
        generiek_product = validated_data.pop("generiek_product")
        doelgroep = data.get("doelgroep")
        catalogus = validated_data.get("catalogus", [])
        product_valt_onder = validated_data.pop("product_valt_onder", [])
        verantwoordelijke_organisatie = data.get("verantwoordelijke_organisatie", [])
        bevoegde_organisatie = validated_data.pop("bevoegde_organisatie", [])
        locaties = validated_data.pop("locaties", [])

        most_recent_version = validated_data.pop("most_recent_version")
        vertalingen = most_recent_version.pop("vertalingen", [])
        publicatie_datum = data.get("publicatie_datum", None)

        if publicatie_datum:
            publicatie_datum = parse_date(publicatie_datum)

        validated_data["generiek_product"] = self.get_generiek_product(
            generiek_product, doelgroep
        )

        if verantwoordelijke_organisatie:
            verantwoordelijke_organisatie = self.get_lokale_overheid(
                verantwoordelijke_organisatie
            )

        if bevoegde_organisatie:
            bevoegde_organisatie = self.get_bevoegde_organisatie(
                bevoegde_organisatie, verantwoordelijke_organisatie
            )

        if not catalogus:
            raise serializers.ValidationError(
                {
                    "catalogus": "Dit is geen geldige URL. U dient een URL op te geven naar de gewenste catalogus of null te gebruiken om automatisch de juiste catalogus te selecteren."
                }
            )

        if isinstance(catalogus, dict):
            validated_data["catalogus"] = self.get_default_catalogus(
                verantwoordelijke_organisatie
            )

        if not validated_data.get("catalogus").is_referentie_catalogus:
            validated_data["referentie_product"] = self.get_referentie_product(
                validated_data["generiek_product"]
            )
        else:
            raise serializers.ValidationError(
                {"catalogus": "U kunt geen referentiecatalogus gebruiken."}
            )

        if product_valt_onder:
            if "generiek_product" in product_valt_onder:
                validated_data["product_valt_onder"] = self.get_product(
                    product_valt_onder["generiek_product"],
                    validated_data["catalogus"],
                )

        if bevoegde_organisatie:
            validated_data["bevoegde_organisatie"] = bevoegde_organisatie
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

        previous_publicatie_datum = product.most_recent_version.publicatie_datum

        versie = self.get_version_number(
            previous_publicatie_datum,
            publicatie_datum,
            product.most_recent_version.versie,
        )

        product_versie, product_versie_created = ProductVersie.objects.update_or_create(
            product=product,
            versie=versie,
            publicatie_datum=None,
            defaults={"publicatie_datum": publicatie_datum},
        )

        if vertalingen:
            for vertaling in vertalingen:

                verwijzing_links = []
                if "verwijzing_links" in vertaling:
                    for verwijzing_link in vertaling["verwijzing_links"]:
                        verwijzing_links.append(list(verwijzing_link.values()))

                vertaling["verwijzing_links"] = verwijzing_links

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
