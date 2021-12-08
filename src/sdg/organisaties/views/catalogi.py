from copy import deepcopy

from django.views.generic import DetailView

from sdg.accounts.mixins import OverheidMixin
from sdg.core.constants import DoelgroepChoices
from sdg.core.models import ProductenCatalogus, Thema
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.models import Product


class CatalogListView(OverheidMixin, DetailView):
    template_name = "organisaties/catalogi/list.html"
    model = LokaleOverheid
    required_roles = ["is_redacteur"]

    def get_lokale_overheid(self):
        self.object = self.get_object()
        return self.object

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        self.object.create_specific_catalogs()

        themes = (
            Thema.objects.all()
            .select_related("informatiegebied")
            .prefetch_related("upn")
        )
        areas_template = {t.informatiegebied.informatiegebied: set() for t in themes}

        catalogs = ProductenCatalogus.objects.specific_catalogs(
            municipality=self.object
        )
        for catalog in catalogs:
            reference_catalog = catalog.referentie_catalogus
            catalog.areas = deepcopy(areas_template)

            products = (
                Product.objects.filter(catalogus=catalog)
                .most_recent()
                .annotate_name()
                .annotate_area()
                .select_generic()
                .exclude(area__isnull=True)
            )
            reference_products = (
                Product.objects.filter(catalogus=reference_catalog)
                .most_recent()
                .annotate_name()
                .annotate_area()
                .select_generic()
                .exclude(area__isnull=True)
            )

            intersected_products = list(
                products | reference_products.exclude(specifieke_producten__in=products)
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

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related("lokaties", "organisatie", "catalogi")
