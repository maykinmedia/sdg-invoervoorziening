from django.db import models
from django.db.models import Q, Value
from django.utils.translation import gettext_lazy as _

from django_filters.rest_framework import FilterSet, filters
from djangorestframework_camel_case.util import camel_to_underscore

from sdg.api.filters import ProductAanwezigChoices
from sdg.core.constants import DoelgroepChoices, TaalChoices
from sdg.core.models import ProductenCatalogus
from sdg.organisaties.models import LokaleOverheid, Lokatie as Locatie
from sdg.producten.models import Product


class ProductenCatalogusFilterSet(FilterSet):
    """Filter for catalogs. Allows filtering by municipality."""

    organisatie = filters.UUIDFilter(
        field_name="lokale_overheid__uuid",
        help_text=_("Toont catalogi die bij de opgegeven organisatie UUID horen."),
    )
    organisatieOwmsIdentifier = filters.CharFilter(
        field_name="lokale_overheid__organisatie__owms_identifier",
        help_text=_(
            "Toont catalogi die bij de opgegeven organisatie OWMS identifier horen."
        ),
    )
    organisatieOwmsPrefLabel = filters.CharFilter(
        field_name="lokale_overheid__organisatie__owms_pref_label",
        help_text=_(
            "Toont catalogi die bij de opgegeven organisatie OWMS pref label horen."
        ),
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
        method="filter_doelgroep",
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
            "Toont producten die behoren tot de catalogus van de opgegeven UUID."
        ),
    )
    publicatieDatum = filters.DateFilter(
        method="filter_publicatie_datum",
        help_text=_(
            "Toont producten met een publicatiedatum groter dan of gelijk aan de opgegeven datum."
        ),
    )
    taal = filters.ChoiceFilter(
        choices=TaalChoices.choices,
        help_text=_("Toont producten die overeenkomen met de opgegeven taal."),
        method="filter_taal",
    )
    upnLabel = filters.CharFilter(
        method="filter_upn", help_text=_("Toont producten met een UPN label")
    )
    upnUri = filters.CharFilter(
        method="filter_upn", help_text=_("Toont producten met een UPN URI")
    )
    organisatieOwmsIdentifier = filters.CharFilter(
        field_name="catalogus__lokale_overheid__organisatie__owms_identifier",
        help_text=_(
            "Toont producten die bij de opgegeven organisatie OWMS identifier horen."
        ),
    )
    organisatieOwmsPrefLabel = filters.CharFilter(
        field_name="catalogus__lokale_overheid__organisatie__owms_pref_label",
        help_text=_(
            "Toont producten die bij de opgegeven organisatie OWMS pref label horen."
        ),
    )

    def filter_product_aanwezig(self, queryset, name, value):
        """:returns: filtered queryset based on `product_aanwezig`'s boolean value."""
        return queryset.all().filter(
            product_aanwezig=ProductAanwezigChoices.get_choice(value).boolean
        )

    def filter_publicatie_datum(self, queryset, name, value):
        """:returns: filtered queryset of products having versions greater than or equal to provided date."""
        if "__" in name:
            _, op = name.split("__")
            return queryset.filter(Q(**{f"versies__publicatie_datum__{op}": value}))

        return queryset.filter(versies__publicatie_datum=value)

    def filter_taal(self, queryset, name, value):
        """:returns: all products for this queryset, annotate the filter value for the inner serializer."""
        return queryset.annotate(
            _filter_taal=Value(value, output_field=models.CharField())
        )

    def filter_upn(self, queryset, name, value):
        """:returns: filtered upn for the given product's UPN."""
        parameter = camel_to_underscore(name)
        return queryset.all().filter(**{f"generiek_product__upn__{parameter}": value})

    def filter_doelgroep(self, queryset, name, value):
        """:returns: filtered doelgroep for the given product's generic product."""
        return queryset.all().filter(**{f"generiek_product__{name}": value})

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

    @classmethod
    def get_filters(cls):
        filters = super().get_filters()
        new_filters = filters.copy()

        for name, filter_ in filters.items():
            if name == "publicatieDatum":
                for op in {"gte"}:
                    filter_.field_name = f"{filter_.field_name}__{op}"
                    new_filters[f"{name}__{op}"] = filter_

        return new_filters


class LocatieFilterSet(FilterSet):
    """Filter for locations. Allows filtering by municipality."""

    organisatie = filters.UUIDFilter(
        field_name="lokale_overheid__uuid",
        help_text=_("Toont locaties die bij de opgegeven organisatie horen."),
    )
    organisatieOwmsIdentifier = filters.CharFilter(
        field_name="lokale_overheid__organisatie__owms_identifier",
        help_text=_(
            "Toont locaties die bij de opgegeven organisatie OWMS identifier horen."
        ),
    )
    organisatieOwmsPrefLabel = filters.CharFilter(
        field_name="lokale_overheid__organisatie__owms_pref_label",
        help_text=_(
            "Toont locaties die bij de opgegeven organisatie OWMS pref label horen."
        ),
    )

    class Meta:
        model = Locatie
        fields = ("organisatie",)


class LokaleOverheidFilterSet(FilterSet):
    """Filter for municipalities. Allows filtering by OWMS identifier."""

    owmsIdentifier = filters.CharFilter(field_name="organisatie__owms_identifier")
    owmsPrefLabel = filters.CharFilter(field_name="organisatie__owms_pref_label")

    class Meta:
        model = LokaleOverheid
        fields = ("owmsIdentifier", "owmsPrefLabel")
