from copy import deepcopy

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

        themes = (
            Thema.objects.all()
            .select_related("informatiegebied")
            .prefetch_related("upn")
        )

        specific_catalogs = ProductenCatalogus.objects.filter(
            lokale_overheid=self.object,
            is_referentie_catalogus=False,
        ).prefetch_related("lokale_overheid__catalogi__referentie_catalogus")

        area_and_products = {
            theme.informatiegebied.informatiegebied: [] for theme in themes
        }
        catalogs = []
        for cat in specific_catalogs:
            ref_cat = cat.referentie_catalogus
            if ref_cat.lokale_overheid == self.object:
                setattr(ref_cat, "area_and_products", deepcopy(area_and_products))
            setattr(cat, "area_and_products", deepcopy(area_and_products))
            catalogs.append(cat)

        for catalog in catalogs:
            reference_catalog = catalog.referentie_catalogus

            products = (
                Product.objects.filter(catalogus=catalog)
                .annotate_name_and_area()
                .select_generic()
            ).exclude(area__isnull=True)
            reference_products = (
                Product.objects.filter(catalogus=reference_catalog)
                .annotate_name_and_area()
                .select_generic()
            ).exclude(area__isnull=True)

            for product in [
                *products,
                *reference_products.exclude(specifieke_producten__in=products),
            ]:
                catalog.area_and_products[product.area].append(product)

            has_reference_catalog = getattr(
                reference_catalog, "area_and_products", False
            )
            if has_reference_catalog:
                for product in reference_products:
                    reference_catalog.area_and_products[product.area].append(product)

        context["catalogs"] = catalogs

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related("lokaties", "organisatie", "catalogi")
