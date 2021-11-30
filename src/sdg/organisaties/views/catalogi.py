from copy import deepcopy

from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.core.models import Thema
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

        # TODO: Optimize / refactor [.->L75]
        themes = (
            Thema.objects.all()
            .select_related("informatiegebied")
            .prefetch_related("upn")
        )
        area_and_products = {
            theme.informatiegebied.informatiegebied: set() for theme in themes
        }
        catalogs = []
        for role in self.request.user.roles.filter(
            is_redacteur=True, lokale_overheid=self.object
        ):
            for cat in role.get_catalogs(reference=False).select_related(
                "referentie_catalogus"
            ):
                ref_cat = cat.referentie_catalogus
                if (
                    ref_cat.user_is_redacteur(self.request.user)
                    and ref_cat.lokale_overheid == self.object
                ):
                    setattr(ref_cat, "area_and_products", deepcopy(area_and_products))
                setattr(cat, "area_and_products", deepcopy(area_and_products))
                catalogs.append(cat)
            for theme in themes.filter(upn__generieke_producten__isnull=False):
                area = theme.informatiegebied.informatiegebied
                for catalog in catalogs:
                    reference_catalog = catalog.referentie_catalogus
                    products = Product.objects.filter(
                        referentie_product__generiek_product__upn__in=theme.upn.all(),
                        catalogus=catalog,
                    )
                    reference_products = Product.objects.filter(
                        generiek_product__upn__in=theme.upn.all(),
                        catalogus=reference_catalog,
                    )
                    catalog.area_and_products[area].update(
                        products
                        | reference_products.exclude(specifieke_producten__in=products)
                    )
                    if getattr(reference_catalog, "area_and_products", None):
                        reference_catalog.area_and_products[area].update(
                            reference_products
                        )

        context["catalogs"] = catalogs

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related("lokaties", "organisatie", "catalogi")
