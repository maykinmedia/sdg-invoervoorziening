from datetime import date

from django.db.models import F, OuterRef, Q, Subquery
from django.utils.translation import ugettext_lazy as _

from django_filters.rest_framework import FilterSet, filters
from djangorestframework_camel_case.util import camel_to_underscore

from sdg.core.constants import DoelgroepChoices, TaalChoices
from sdg.core.models import ProductenCatalogus
from sdg.organisaties.models import LokaleOverheid, Lokatie
from sdg.producten.models import Product, ProductVersie


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

    def filter_publicatie_datum(self, queryset, name, value):
        """:returns: products having versions greater than or equal to provided date."""
        return queryset.all().filter(versies__publicatie_datum__gte=value)

    def filter_taal(self, queryset, name, value):
        """:returns: filtered queryset for the given products containing translations for given language."""
        active_version_qs = (
            ProductVersie.objects.filter(
                product=OuterRef("pk"),
                publicatie_datum__lte=date.today(),
            )
            .order_by("-versie")
            .values("pk")[:1]
        )
        language_qs = ProductVersie.objects.filter(
            pk=OuterRef("active_version"),
            vertalingen__taal=value,
        ).values("pk")

        queryset = queryset.filter(versies__in=Subquery(active_version_qs)).annotate(
            active_version=F("versies")
        )
        queryset = queryset.filter(versies__in=Subquery(language_qs))

        return queryset

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
