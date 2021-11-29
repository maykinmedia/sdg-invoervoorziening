from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from django_filters.rest_framework import FilterSet, filters
from djangorestframework_camel_case.util import camel_to_underscore

from sdg.api.filters import ProductAanwezigChoices
from sdg.core.constants import DoelgroepChoices
from sdg.core.models import ProductenCatalogus
from sdg.organisaties.models import LokaleOverheid, Lokatie
from sdg.producten.models import Product


class ProductenCatalogusFilterSet(FilterSet):
    """Filter for catalogs. Allows filtering by municipality."""

    organisatie = filters.UUIDFilter(
        field_name="lokale_overheid__uuid",
        help_text=_("Toont catalogi die bij de opgegeven organisatie horen."),
    )

    class Meta:
        model = ProductenCatalogus
        fields = ("organisatie",)


class ProductFilterSet(FilterSet):
    """Filter for products. Allows filtering by organization, target-group, catalog, publication date."""

    organisatie = filters.UUIDFilter(
        field_name="catalogus__lokale_overheid__uuid",
        help_text=_("Toont producten die bij de opgegeven organisatie horen."),
    )
    doelgroep = filters.ChoiceFilter(
        choices=DoelgroepChoices.choices,
        help_text=_("Toont producten die overeenkomen met de opgegeven doelgroepen."),
        lookup_expr="icontains",
    )
    productAanwezig = filters.ChoiceFilter(
        choices=ProductAanwezigChoices.choices,
        help_text=_("Toont producten die aanwezig zijn in de opgegeven catalogus."),
        method="filter_product_aanwezig",
    )
    catalogus = filters.UUIDFilter(
        field_name="catalogus__uuid",
        help_text=_(
            "Toont producten die behoren tot de catalogus van de opgegeven uuid."
        ),
    )
    publicatieDatum = filters.DateFilter(
        method="filter_publicatie_datum",
        help_text=_(
            "Toont producten met een publicatiedatum groter dan of gelijk aan de opgegeven datum."
        ),
    )
    upnLabel = filters.CharFilter(
        method="filter_upn", help_text=_("Toont producten met een UPN label")
    )
    upnUri = filters.CharFilter(
        method="filter_upn", help_text=_("Toont producten met een UPN URI")
    )

    def filter_product_aanwezig(self, queryset, name, value):
        """:returns: filtered queryset based on `product_aanwezig`'s boolean value."""
        value = value.lower()
        return queryset.all().filter(
            product_aanwezig=ProductAanwezigChoices.get_choice(value).boolean
        )

    def filter_publicatie_datum(self, queryset, name, value):
        """:returns: filtered queryset of products having versions greater than or equal to provided date."""
        return queryset.all().filter(versies__publicatie_datum__gte=value)

    def filter_upn(self, queryset, name, value):
        """:returns: filtered queryset for the given product's UPN."""
        parameter = camel_to_underscore(name)
        return queryset.all().filter(
            Q(**{f"generiek_product__upn__{parameter}": value})
            | Q(**{f"referentie_product__generiek_product__upn__{parameter}": value})
        )

    class Meta:
        model = Product
        fields = (
            "organisatie",
            "doelgroep",
            "catalogus",
            "publicatieDatum",
            "upnLabel",
            "upnUri",
        )


class LokatieFilterSet(FilterSet):
    """Filter for locations. Allows filtering by municipality."""

    organisatie = filters.UUIDFilter(
        field_name="lokale_overheid__uuid",
        help_text=_("Toont locaties die bij de opgegeven organisatie horen."),
    )

    class Meta:
        model = Lokatie
        fields = ("organisatie",)


class LokaleOverheidFilterSet(FilterSet):
    """Filter for municipalities. Allows filtering by OWMS identifier."""

    owmsIdentifier = filters.CharFilter(field_name="organisatie__owms_identifier")
    owmsPrefLabel = filters.CharFilter(field_name="organisatie__owms_pref_label")

    class Meta:
        model = LokaleOverheid
        fields = ("owmsIdentifier", "owmsPrefLabel")
