from django.utils.translation import ugettext_lazy as _

from django_filters.rest_framework import FilterSet, filters

from sdg.core.models import ProductenCatalogus
from sdg.organisaties.models import Lokatie
from sdg.producten.models import Product


class ProductenCatalogusFilterSet(FilterSet):
    """Filter for catalogs. Allows filtering by municipality."""

    organisatie = filters.CharFilter(
        field_name="lokale_overheid__organisatie__owms_pref_label",
        help_text=_("Toont catalogi die bij de opgegeven organisatie horen."),
        min_length=1,
        max_length=200,
    )

    class Meta:
        model = ProductenCatalogus
        fields = ("lokale_overheid",)


class ProductFilterSet(FilterSet):
    """Filter for products. Allows filtering by organization, target-group, catalog, publication date."""

    organisatie = filters.CharFilter(
        field_name="catalogus__lokale_overheid__organisatie__owms_pref_label",
        help_text=_("Toont producten die bij de opgegeven organisatie horen."),
        min_length=1,
        max_length=200,
    )
    doelgroep = filters.CharFilter(
        lookup_expr="icontains",
        help_text=_("Toont producten die overeenkomen met de opgegeven doelgroepen."),
    )
    catalogus_uuid = filters.UUIDFilter(
        field_name="catalogus__uuid",
        help_text=_(
            "Toont producten die behoren tot de catalogus van de opgegeven uuid."
        ),
    )
    publicatie_datum = filters.DateFilter(
        method="filter_publicatie_datum",
        help_text=_(
            "Toont producten met een publicatiedatum groter dan of gelijk aan de opgegeven datum."
        ),
    )

    def filter_publicatie_datum(self, queryset, name, value):
        return queryset.all().filter(versies__publicatie_datum__gte=value)

    class Meta:
        model = Product
        fields = (
            "organisatie",
            "doelgroep",
            "catalogus_uuid",
            "publicatie_datum",
        )


class LokatieFilterSet(FilterSet):
    """Filter for locations. Allows filtering by municipality."""

    organisatie = filters.CharFilter(
        field_name="lokale_overheid__organisatie__owms_pref_label",
        help_text=_("Toont locaties die bij de opgegeven organisatie horen."),
        min_length=1,
        max_length=200,
    )

    class Meta:
        model = Lokatie
        fields = ("lokale_overheid",)
