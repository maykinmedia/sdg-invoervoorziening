from django.views.generic import DetailView

from sdg.accounts.mixins import OverheidMixin
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

        catalogs = ProductenCatalogus.objects.specific_catalogs(
            municipality=self.object
        ).annotate_area_and_products()
        for catalog in catalogs:
            reference_catalog = catalog.referentie_catalogus

            products = (
                Product.objects.filter(catalogus=catalog)
                .most_recent()
                .annotate_name_and_area()
                .select_generic()
                .exclude(area__isnull=True)
            )
            reference_products = (
                Product.objects.filter(catalogus=reference_catalog)
                .most_recent()
                .annotate_name_and_area()
                .select_generic()
                .exclude(area__isnull=True)
            )

            intersected_products = list(
                products | reference_products.exclude(specifieke_producten__in=products)
            )

            for product in intersected_products:
                catalog.area_and_products[product.area].add(product)

            reference_areas = getattr(reference_catalog, "area_and_products", None)
            if reference_areas:
                for product in reference_products:
                    reference_areas[product.area].add(product)

        context["catalogs"] = catalogs
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related("lokaties", "organisatie", "catalogi")
