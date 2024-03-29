import datetime

from django.db import transaction
from django.utils.dateparse import parse_date

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
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
from sdg.producten.models import (
    GeneriekProductOverheidsorganisatieRol,
    LocalizedGeneriekProduct,
    LocalizedProduct,
    Product,
    ProductVersie,
)
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
                "help_text": "De inleidende tekst voor het product. Hierin kunt u het product beschrijven en komt direct na de generieke productbeschrijving. Dit veld ondersteunt Markdown.",
            },
            "procedure_beschrijving": {
                "help_text": "De beschrijving van hoe het product wordt aangevraagd. Dit veld ondersteunt Markdown."
            },
            "bewijs": {
                "help_text": "Dit bevat de bewijsstukken die de burger of ondernemer nodig heeft om dit product aan te vragen. Dit veld ondersteunt Markdown."
            },
            "vereisten": {
                "help_text": "Dit zijn de voorwaarden voor het aanvragen van het product. Dit veld ondersteunt Markdown."
            },
            "bezwaar_en_beroep": {
                "help_text": "Beschrijft hoe de burger of ondernemer bezwaar kan maken. Dit veld ondersteunt Markdown."
            },
            "kosten_en_betaalmethoden": {
                "help_text": "Beschrijft hoe de burger of ondernemer kan betalen en wat de kosten zijn. Dit veld ondersteunt Markdown."
            },
            "uiterste_termijn": {
                "help_text": "De informatie over hoe hoelang het duurt voor het aanvragen van dit product. Dit doet u aan de hand van werkdagen/weken. Dit veld ondersteunt Markdown."
            },
            "wtd_bij_geen_reactie": {
                "help_text": "Beschrijft wat de aanvrager moet doen bij geen reactie. Dit veld ondersteunt Markdown."
            },
            "product_aanwezig_toelichting": {
                "help_text": "Een optioneel veld om uit te leggen waarom het product niet aanwezig is. Deze moet u alleen invullen als u het product niet levert en dan is dit veld verplicht! Dit veld ondersteunt Markdown."
            },
            "product_valt_onder_toelichting": {
                "help_text": "Een optioneel veld om uit te leggen waarom dit product onder een andere product valt. Deze moet u alleen invullen als dit product onder een andere product valt en dan is dit veld verplicht! Dit veld ondersteunt Markdown."
            },
            "datum_wijziging": {
                "help_text": "Datum wanneer dit product voor het laatst is gewijzigd."
            },
        }

    def to_representation(self, instance):
        """
        Extend ``to_representation`` to add aditional logic:

        Hide data from ``product_valt_onder_toelichting`` if ``product_valt_onder`` is empty.
        Hide data from ``product_aanwezig_toelichting`` if ``product_aanwezig`` is True.
        """

        data = super().to_representation(instance)

        product = instance.product_versie.product

        if not product.product_valt_onder:
            data["product_valt_onder_toelichting"] = ""

        if product.product_aanwezig:
            data["product_aanwezig_toelichting"] = ""

        return data


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
    # The doelgroep is an essential part to identify a product with well-known
    # properties (organisation, UPN and doelgroep) but this would lead to the
    # question if we also need this to identify "productValtOnder".
    #
    # doelgroep = serializers.ChoiceField(
    #     source="generiek_product.doelgroep",
    #     choices=DoelgroepChoices.choices,
    #     required=True,
    #     help_text="De doelgroep van dit product.",
    # )

    class Meta:
        model = Product
        fields = (
            "url",
            "upn_uri",
            "upn_label",
            # "doelgroep",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:product-detail",
                "lookup_field": "uuid",
                "help_text": "De unieke URL van dit object binnen deze API.",
            }
        }


class ProductLocatieSerializer(LocatieBaseSerializer):
    openingstijden = OpeningstijdenSerializer(source="*", read_only=True)

    class Meta(LocatieBaseSerializer.Meta):
        read_only_fields = (
            "url",
            "uuid",
            "straat",
            "nummer",
            "postcode",
            "plaats",
            "land",
            "openingstijden_opmerking",
        )
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
        source="organisatie.owms_identifier",
        help_text="De OWMS Identifier van de hoofdorganisatie van deze lokale overheid.",
        required=True,
    )
    owms_pref_label = serializers.CharField(
        source="organisatie.owms_pref_label",
        help_text="OWMS label van de hoofdorganisatie van deze lokale overheid.",
        required=False,
    )
    owms_end_date = serializers.DateTimeField(
        source="organisatie.owms_end_date",
        help_text="De einddatum, zoals gevonden in het OWMS-model.",
        read_only=True,
        required=False,
    )

    class Meta:
        model = LokaleOverheid
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
            [str(instance.uuid)],
            request=self.context["request"],
        )


class ProductSerializer(ProductBaseSerializer):
    """Serializer for a product, including UPN, availability, locations and latest version translations."""

    verantwoordelijke_organisatie = ProductLokaleOverheidSerializer(
        source="catalogus.lokale_overheid"
    )
    publicatie_datum = serializers.DateField(
        allow_null=True,
        help_text="De datum die aangeeft wanneer het product gepubliceerd is/wordt.",
    )
    product_aanwezig = serializers.BooleanField(
        allow_null=True,
        required=True,
        help_text="Een boolean die aangeeft of de organisatie dit product levert of niet. Als de verantwoordelijke organisatie niet expliciet heeft aangegeven dat een product aanwezig of afwezig is, dan is deze waarde `null`. Als een product afwezig is, dan moet er een toelichting worden gegeven in alle beschikbare talen. Alle andere vertaalde velden kunnen dan leeg blijven.",
    )
    vertalingen = LocalizedProductSerializer(
        many=True,
        # In case there is no active version, there are no available
        # translations. Hence, we allow null here (which affect the GET
        # operation to actually work).
        allow_null=True,
        help_text="Een lijst met specifieke teksten op basis van taal.",
    )
    beschikbare_talen = serializers.SerializerMethodField(
        method_name="get_talen",
        help_text="Alle beschikbare talen.",
    )
    versie = serializers.IntegerField(
        help_text="De huidige versie van dit product.",
        default=0,
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
        version_fields = (
            "vertalingen",
            "publicatie_datum",
            "versie",
        )

    def get_fields(self):
        """
        Dynamically bind the source of certain fields based on the version of the product.
        """
        fields = super().get_fields()

        for field in self.Meta.version_fields:
            fields[field].source = f"{self.version_property_name}.{field}"

        return fields

    @property
    def version_property_name(self):
        """
        Return the appropriate version property based on the meta headers.

        If the token type is designed for editors, return the most recent version.
        In other cases return the active version.
        """

        request = self.context.get("request", object)
        auth = getattr(request, "auth", None)

        if auth and auth.api_default_most_recent:
            return "most_recent_version"

        return "active_version"

    def get_talen(self, obj: Product) -> list:
        return TaalChoices.get_available_languages()

    def to_representation(self, instance):
        data = super(ProductBaseSerializer, self).to_representation(instance)
        version = getattr(instance, self.version_property_name, None)

        if version and getattr(instance, "_filter_taal", None):
            translations = version.vertalingen.all()
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

        version = attrs[self.version_property_name]

        languages = [t["taal"] for t in version["vertalingen"]]
        required_languages = TaalChoices.get_available_languages()
        if any(lang not in languages for lang in required_languages):
            raise serializers.ValidationError(
                {
                    "vertalingen": f"Het veld 'taal' is verplicht. Geldige waarden zijn: {required_languages}"
                }
            )

        if not attrs["product_aanwezig"]:
            for translation in version["vertalingen"]:
                if (
                    not translation["product_aanwezig_toelichting"]
                    or translation["product_aanwezig_toelichting"] == ""
                ):
                    raise serializers.ValidationError(
                        {
                            "productAanwezigToelichting": "Het veld 'productAanwezigToelichting' is verplicht als het product niet aanwezig is."
                        }
                    )

        if attrs["product_valt_onder"]:
            for translation in version["vertalingen"]:
                if (
                    not translation["product_valt_onder_toelichting"]
                    or translation["product_valt_onder_toelichting"] == ""
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
                        "": "De combinatie van waarden in de velden 'upnUri' en 'doelgroep' is ongeldig. Het object met deze waarden bestaat niet."
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

    def get_product(self, product_valt_onder, catalogus, doelgroep):
        try:
            return Product.objects.get(
                generiek_product__upn__upn_uri=product_valt_onder["upn_uri"],
                generiek_product__doelgroep=doelgroep,
                catalogus=catalogus,
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "productValtOnder": "De waarde van het veld 'upnUri' is ongeldig binnen deze 'catalogus' en 'doelgroep'. Het object met deze waarde bestaat niet."
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

        raise serializers.ValidationError(
            {
                "verantwoordelijkeOrganisatie": "De gegeven waarde was incorect de mogelijke veld opties zijn 'naam' en 'owmsIdentifier'."
            }
        )

    def should_create_new_version(self, previous_date, new_date):
        today = datetime.date.today()

        if previous_date is None:
            return False

        if new_date is None and previous_date <= today:
            return True

        if new_date is None and previous_date > today:
            return False

        if new_date < previous_date and new_date < today:
            raise serializers.ValidationError(
                {
                    "publicatieDatum": "Het product kan niet een vroegere publicatiedatum krijgen dan een voorgaande versie."
                }
            )

        if previous_date <= today:
            return True

        return False

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
                try:
                    overheid_locatie = Locatie.objects.get(
                        naam=locatie["naam"],
                        lokale_overheid__organisatie=catalogus.lokale_overheid.organisatie,
                    )
                except Locatie.DoesNotExist:
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

        version = validated_data.get(self.version_property_name, {})
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
            validated_data["bevoegde_organisatie"] = self.get_bevoegde_organisatie(
                bevoegde_organisatie, verantwoordelijke_organisatie
            )

        else:
            validated_data["bevoegde_organisatie"] = BevoegdeOrganisatie.objects.get(
                lokale_overheid=verantwoordelijke_organisatie,
                organisatie=verantwoordelijke_organisatie.organisatie,
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
                    doelgroep,
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

        if self.should_create_new_version(
            previous_publicatie_datum,
            publicatie_datum,
        ):
            product_versie = ProductVersie.objects.create(
                product=product,
                versie=product.most_recent_version.versie + 1,
                publicatie_datum=publicatie_datum,
            )
            product_versie_created = True
        else:
            product_versie = product.most_recent_version
            product_versie.publicatie_datum = publicatie_datum
            product_versie.save()

            product_versie_created = False

        for translation in version.get("vertalingen", []):
            verwijzing_links = []
            if "verwijzing_links" in translation:
                for verwijzing_link in translation["verwijzing_links"]:
                    verwijzing_links.append(list(verwijzing_link.values()))

            translation["verwijzing_links"] = verwijzing_links

            if product_versie_created:

                LocalizedProduct.objects.create(
                    **translation,
                    product_versie=product_versie,
                )

            else:
                translation["product_versie"] = product_versie
                localized_product_qs = LocalizedProduct.objects.filter(
                    product_versie=product_versie, taal=translation["taal"]
                )
                localized_product_qs.update(**translation)

        return product


class GeneriekProductLinkSerializer(serializers.ModelSerializer):
    label = serializers.CharField(help_text="Linktekst")
    url = serializers.URLField(help_text="Link URL")
    categorie = serializers.URLField(
        help_text="Link categorie. Dit zijn de mogelijke categorieën: intern, extern, wetgeving en wetswijziging"
    )

    class Meta:
        model = LocalizedGeneriekProduct
        fields = ("label", "url", "categorie")

    def to_representation(self, value):
        return dict(
            zip(
                self.Meta.fields,
                value,
            )
        )


class GeneriekProductOrganisatieSerializer(serializers.ModelSerializer):
    owms_uri = serializers.URLField(
        source="overheidsorganisatie.owms_identifier", help_text="OWMS URI"
    )
    owms_pref_label = serializers.URLField(
        source="overheidsorganisatie.owms_pref_label", help_text="OWMS PrefLabel"
    )

    class Meta:
        model = GeneriekProductOverheidsorganisatieRol
        fields = (
            "rol",
            "owms_pref_label",
            "owms_uri",
        )
        extra_kwargs = {
            "rol": {
                "help_text": "Rol van organisatie",
            },
        }


class GeneriekProductSerializer(serializers.ModelSerializer):
    titel = serializers.CharField(
        source="product_titel", help_text="Titel van het product"
    )
    tekst = serializers.CharField(
        source="generieke_tekst", help_text="Tekst van het product"
    )
    links = serializers.ListField(
        source="verwijzing_links",
        child=GeneriekProductLinkSerializer(),
        help_text="Linkverwijzingen",
    )
    organisaties = serializers.ListField(
        source="generiek_product.generiekproductoverheidsorganisatierol_set.all",
        child=GeneriekProductOrganisatieSerializer(),
        help_text="Organisaties",
    )
    laatst_gecheckt = serializers.DateTimeField(
        source="datum_check",
        help_text="Laatst gecheckt datum. Datum heeft het formaat {datum}T{tijd}",
    )
    upn_uri = serializers.URLField(
        source="generiek_product.upn_uri", help_text="UPN URI van het product"
    )
    upn_label = serializers.CharField(
        source="generiek_product.upn_label", help_text="UPN label van het product"
    )
    doelgroep = serializers.CharField(
        source="generiek_product.doelgroep", help_text="De SDG doelgroep indicatie"
    )

    class Meta:
        model = LocalizedGeneriekProduct
        fields = (
            "url",
            "uuid",
            "upn_uri",
            "upn_label",
            "doelgroep",
            "taal",
            "titel",
            "tekst",
            "landelijke_link",
            "links",
            "organisaties",
            "laatst_gecheckt",
            "laatst_gewijzigd",
        )
        extra_kwargs = {
            "url": {
                "view_name": "api:generic-product-detail",
                "lookup_field": "uuid",
                "help_text": "De unieke URL van dit object binnen deze API.",
            },
            "laatst_gewijzigd": {
                "help_text": "Laatst gewijzigd datum. Datum heeft het formaat {datum}T{tijd}"
            },
            "landelijke_link": {
                "help_text": "URL van het product op de nationale portalen website"
            },
        }
