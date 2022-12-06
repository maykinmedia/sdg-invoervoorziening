import datetime

from django.db import transaction

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from sdg.api.serializers.fields import LabeledUrlListField
from sdg.api.serializers.producten import (
    ProcedureLink,
    ProductBaseSerializer,
    ProductLocatieSerializer,
)
from sdg.core.constants.product import TaalChoices
from sdg.organisaties.models import Lokatie as Locatie
from sdg.producten.models import LocalizedProduct, Product, ProductVersie


from rest_framework.reverse import reverse


class CustomVertalingenHyperLink(serializers.HyperlinkedRelatedField):
    view_name = "api:vertalingen-list"

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            "product_uuid": obj.product_versie.product.uuid,
            "versie": obj.product_versie.versie,
            "taal": obj.taal,
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            "product_verise__product__uuid": view_kwargs["product_uuid"],
            "product_versie__versie": view_kwargs["versie"],
            "taal": view_kwargs["taal"],
        }
        return self.get_queryset().get(**lookup_kwargs)


class ProductVersieSingleSerializer(ProductBaseSerializer):
    product_valt_onder = ProductBaseSerializer(
        allow_null=True,
        required=True,
        help_text="Als een product valt onder een ander product (het product wordt bijvoorbeeld geleverd middels een ander product), dan staat deze hier vermeld. Als een product onder een ander product valt, dan moet er een toelichting worden gegeven in alle beschikbare talen. Alle andere vertaalde velden kunnen dan leeg blijven.",
    )
    locaties = ProductLocatieSerializer(
        allow_null=True,
        many=True,
        help_text="Een lijst met locaties waarop dit product beschikbaar is.",
    )
    versie = SerializerMethodField(
        method_name="get_versie", help_text="De huidige versie van dit product."
    )
    publicatie_datum = SerializerMethodField(
        method_name="get_datum",
        help_text="De datum wanneer dit product gepubliseerd is/wordt.",
    )
    talen = CustomVertalingenHyperLink(
        source="most_recent_version.vertalingen",
        view_name="api:vertalingen-detail",
        read_only=True,
        many=True,
    )

    class Meta:
        model = Product
        fields = (
            "url",
            "product_aanwezig",
            "product_valt_onder",
            "locaties",
            "versie",
            "publicatie_datum",
            "talen",
        )
        extra_kwargs = {
            "product_aanwezig": {"required": True},
            "url": {
                "view_name": "api:product-detail",
                "lookup_field": "uuid",
                "help_text": "De unieke URL van dit object binnen deze API.",
            },
        }

    @staticmethod
    def _get_most_recent_version(product: Product, field_name, default=None):
        """Get the value of a field from the product's active version."""
        most_recent_version = getattr(product, "most_recent_version", None)
        return (
            getattr(most_recent_version, field_name) if most_recent_version else default
        )

    def get_versie(self, obj: Product) -> int:
        return self._get_most_recent_version(obj, "versie", default=0)

    def get_datum(self, obj: Product) -> int:
        return self._get_most_recent_version(obj, "publicatie_datum", default=0)

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
                    "upnUri": "De waarde van het veld 'upnUri' is ongeldig. Het object met deze waarde bestaat niet."
                }
            )
        except KeyError:
            raise serializers.ValidationError(
                {"upnUri": "Het veld 'upnUri' is verplicht."}
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
        product_uuid = self.context["view"].kwargs["product_uuid"]
        product_valt_onder = validated_data.pop("product_valt_onder", None)
        locaties = validated_data.pop("locaties", None)

        product = Product.objects.get(uuid=product_uuid)
        most_recent_version = product.most_recent_version
        versie = most_recent_version.versie

        if (
            most_recent_version.publicatie_datum is not None
            and most_recent_version.publicatie_datum <= datetime.date.today()
        ):
            product_versie = ProductVersie.objects.create(
                versie=versie + 1, product=product, publicatie_datum=None
            )
            for taal in TaalChoices.values:
                LocalizedProduct.objects.create(
                    product_versie=product_versie,
                    taal=taal,
                )
        else:
            product_versie = ProductVersie.objects.get(product=product, versie=versie)

        if product_valt_onder:
            if "generiek_product" in product_valt_onder:
                validated_data["product_valt_onder"] = self.get_product(
                    product_valt_onder["generiek_product"],
                    product.catalogus,
                    product.generiek_product.doelgroep,
                )
        else:
            validated_data["product_valt_onder"] = None

        super().update(product, validated_data)

        product.locaties.set(
            self.get_locaties(
                locaties,
                product.catalogus,
            )
        )

        return product


class ProductVersieVertalingenSerializer(ProductBaseSerializer):
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
                "help_text": """De taal van de onderstaande gegevens volgens formaat [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes).""",
                "read_only": True,
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
                "help_text": "Een optioneel veld om uit te leggen waarom dit product onder een andere product valt. Deze moet u alleen invullen als dit product onder een andere product valt en dan is dit veld verplicht! Dit veld ondersteund Markdown.",
            },
            "datum_wijziging": {
                "help_text": "Datum wanneer dit product voor het laatst is gewijzigd."
            },
        }

    def validate(self, attrs):
        product_uuid = self.context["view"].kwargs["product_uuid"]
        versie = int(self.context["view"].kwargs["versie"])
        taal = self.context["view"].kwargs["taal"]

        product = Product.objects.get(uuid=product_uuid)
        try:
            product_versie = ProductVersie.objects.get(product=product, versie=versie)
        except ProductVersie.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "": f"De meegegeven versie nummer is verkeerd, het nummer moet '{product.most_recent_version.versie}' zijn"
                }
            )

        if product.most_recent_version.versie is not product_versie.versie:
            raise serializers.ValidationError(
                {
                    "": f"De meegegeven versie nummer is verkeerd, het nummer moet '{product.most_recent_version.versie}' zijn"
                }
            )

        if (
            product_versie.publicatie_datum is not None
            and product_versie.publicatie_datum <= datetime.date.today()
        ):
            raise serializers.ValidationError(
                {"": "Het product dat u probeert aan tepassen is geen concept."}
            )

        if taal not in TaalChoices.values:
            raise serializers.ValidationError(
                {"taal": f"Taal moet een instantie van {TaalChoices.values} zijn."}
            )

        if product.product_aanwezig is False:
            try:
                if not attrs["product_aanwezig_toelichting"]:
                    raise serializers.ValidationError(
                        {
                            "productAanwezigToelichting": "ProductAanwezigToelichting moet ingevult zijn zolang productAanwezig op 'false' staat."
                        }
                    )
            except KeyError:
                raise serializers.ValidationError(
                    {
                        "productAanwezigToelichting": "productAanwezigToelichting is verplicht zolang productAanwezig op 'false' staat."
                    }
                )

        if product.product_aanwezig is True:
            if "product_aanwezig_toelichting" in attrs:
                if attrs["product_aanwezig_toelichting"]:
                    raise serializers.ValidationError(
                        {
                            "productAanwezigToelichting": "ProductAanwezigToelichting moet niet ingevult zijn zolang productAanwezig op 'true' staat."
                        }
                    )

        if product.product_valt_onder is not None:
            try:
                if not attrs["product_valt_onder_toelichting"]:
                    raise serializers.ValidationError(
                        {
                            "productValtOnderToelichting": "ProductValtOnderToelichting moet ingevult zijn zolang productValtOnder niet op 'null' staat."
                        }
                    )
            except KeyError:
                raise serializers.ValidationError(
                    {
                        "productValtOnderToelichting": "ProductValtOnderToelichting is verplicht zolang productValtOnder niet op 'null' staat."
                    }
                )

        if product.product_valt_onder is None:
            if "product_valt_onder_toelichting" in attrs:
                if attrs["product_valt_onder_toelichting"]:
                    raise serializers.ValidationError(
                        {
                            "productValtOnderToelichting": "ProductValtOnderToelichting moet niet ingevult zijn zolang productValtOnder op 'null' staat."
                        }
                    )

        return super().validate(attrs)

    @transaction.atomic
    def update(self, instance, validated_data):
        verwijzing_links = []
        if "verwijzing_links" in validated_data:
            for verwijzing_link in validated_data["verwijzing_links"]:
                verwijzing_links.append(list(verwijzing_link.values()))

        validated_data["verwijzing_links"] = verwijzing_links

        return super().update(instance, validated_data)


class ProductVersiePublishSerializer(ProductBaseSerializer):
    product_valt_onder = ProductBaseSerializer(
        read_only=True,
        source="product.product_valt_onder",
        help_text="Als een product valt onder een ander product (het product wordt bijvoorbeeld geleverd middels een ander product), dan staat deze hier vermeld. Als een product onder een ander product valt, dan moet er een toelichting worden gegeven in alle beschikbare talen. Alle andere vertaalde velden kunnen dan leeg blijven.",
    )
    locaties = ProductLocatieSerializer(
        read_only=True,
        many=True,
        source="product.locaties",
        help_text="Een lijst met locaties waarop dit product beschikbaar is.",
    )

    class Meta:
        model = ProductVersie
        fields = (
            "publicatie_datum",
            "product_valt_onder",
            "locaties",
            "versie",
        )
        extra_kwargs = {
            "publicatie_datum": {"required": False},
            "versie": {"read_only": True},
        }

    def validate(self, attrs):
        product = self.context.get("product")
        product_versie = self.context.get("product_versie")

        if product.most_recent_version.versie is not product_versie.versie:
            raise serializers.ValidationError(
                {
                    "": f"De meegegeven versie nummer is verkeerd, het nummer moet '{product.most_recent_version.versie}' zijn"
                }
            )

        if (
            product_versie.publicatie_datum is not None
            and product_versie.publicatie_datum <= datetime.date.today()
        ):
            raise serializers.ValidationError(
                {
                    "": "Een gepubliceerde product kan niet nog een keer gepubliseerd worden."
                }
            )

        if product.product_aanwezig is None:
            raise serializers.ValidationError(
                {"": "productAanwezig moet op 'true' of op 'false' staan."}
            )

        if product.product_aanwezig is True:
            for vertaling in product_versie.vertalingen.all():
                if vertaling.product_aanwezig_toelichting:
                    raise serializers.ValidationError(
                        {
                            "": "ProductAanwezigToelichting moet niet ingevult zijn zolang productAanwezig op 'true' staat."
                        }
                    )

        if product.product_aanwezig is False:
            for vertaling in product_versie.vertalingen.all():
                if not vertaling.product_aanwezig_toelichting:
                    raise serializers.ValidationError(
                        {
                            "": "ProductAanwezigToelichting moet ingevult zijn zolang productAanwezig op 'false' staat."
                        }
                    )

        if product.product_valt_onder is not None:
            for vertaling in product_versie.vertalingen.all():
                if not vertaling.product_valt_onder_toelichting:
                    raise serializers.ValidationError(
                        {
                            "": "ProductValtOnderToelichting moet ingevult zijn zolang productValtOnder niet op 'null' staat."
                        }
                    )

        if product.product_valt_onder is None:
            for vertaling in product_versie.vertalingen.all():
                if vertaling.product_valt_onder_toelichting:
                    raise serializers.ValidationError(
                        {
                            "": "ProductValtOnderToelichting moet niet ingevult zijn zolang productValtOnder op 'null' staat."
                        }
                    )

        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        publicatie_datum = validated_data.get("publicatie_datum", datetime.date.today())
        product_versie = self.context.get("product_versie")

        product_versie.publicatie_datum = publicatie_datum
        product_versie.save()

        return product_versie
