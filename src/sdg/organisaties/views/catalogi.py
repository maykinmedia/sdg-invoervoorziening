from copy import deepcopy

from django.views.generic import ListView

from sdg.accounts.mixins import OverheidMixin
from sdg.core.constants import DoelgroepChoices
from sdg.core.models import ProductenCatalogus, Thema
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.models import Product


class CatalogListView(OverheidMixin, ListView):
    template_name = "organisaties/catalogi/list.html"
    model = ProductenCatalogus
    required_roles = ["is_redacteur"]

    def get_lokale_overheid(self):
        self.lokale_overheid = LokaleOverheid.objects.get(pk=self.kwargs["pk"])
        self.object_list = (
            self.get_queryset()
            .select_related("lokale_overheid")
            .filter(
                lokale_overheid=self.lokale_overheid,
            )
        )
        return self.lokale_overheid

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        if self.lokale_overheid.automatisch_catalogus_aanmaken:
            self.object_list.create_specific_catalogs(municipality=self.lokale_overheid)

        themes = (
            Thema.objects.all()
            .select_related("informatiegebied")
            .prefetch_related("upn")
        )
        areas_template = {t.informatiegebied.informatiegebied: set() for t in themes}

        catalogs = self.object_list.specific_catalogs()
        for catalog in catalogs:
            reference_catalog = catalog.referentie_catalogus
            catalog.areas = deepcopy(areas_template)

            products = Product.objects.filter(catalogus=catalog)
            reference_products = Product.objects.filter(catalogus=reference_catalog)
            products, reference_products = (
                _apply_filters(queryset) for queryset in (products, reference_products)
            )

            intersected_products = products | reference_products.exclude(
                specifieke_producten__in=products
            )

            for product in intersected_products:
                catalog.areas[product.area].add(product)

            if catalog.municipality_owns_reference:
                reference_catalog.areas = deepcopy(areas_template)
                for product in reference_products:
                    reference_catalog.areas[product.area].add(product)

        context["catalogs"] = catalogs
        context["group_choices"] = DoelgroepChoices.choices
        return context


def _apply_filters(queryset):
    """Apply common filter/annotations/selects to queryset of products."""
    return (
        queryset.most_recent()
        .annotate_name()
        .annotate_area()
        .select_generic()
        .select_related("catalogus__lokale_overheid")
        .exclude(area__isnull=True)
    )
