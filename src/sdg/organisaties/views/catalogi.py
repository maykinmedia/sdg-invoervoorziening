from django.db.models import Case, When, Value
from django.db.models import F, Max
from django.utils.translation import gettext as _

from rijkshuisstijl.views.generic import ListView as RHListView

from sdg.accounts.mixins import OverheidMixin
from sdg.core.models import ProductenCatalogus
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.models import Product


class CatalogListView(OverheidMixin, RHListView):
    fields = [
        {"key": "_name", "label": _("Naam")},
        {
            "key": "referentie_product__generiek_product__upn__thema__informatiegebied",
            "label": _("Informatiegebied"),
        },
        {"label": _("Aanwezig"), "key": "product_aanwezig"},
        {
            "key": "doelgroep",
            "label": _("Doelgroep"),
        },
        {
            "key": "_latest_publication_date",
            "label": _("Publicatie datum"),
        },
    ]
    filterable_columns = [
        # FIXME: Labels don't seem to override the default labels
        {"key": "_name", "label": _("Zoek op productnaam")},
        {
            "key": "referentie_product__generiek_product__upn__thema__informatiegebied",
            "label": _("Thema"),
        },
        {"key": "product_aanwezig", "label": _("Aanwezig")},
        {
            "key": "doelgroep",
            "label": _("Doelgroep"),
        },
    ]

    model = Product
    required_roles = ["is_beheerder", "is_redacteur"]
    template_name = "organisaties/catalogi/list.html"
    paginate_by = 100

    def get_datagrid_config(self):
        config = {
            **super().get_datagrid_config(),
            "dom_filter": True,
        }
        return config

    def get_lokale_overheid(self):
        """
        Returns the LokaleOverheid object for local municipality.
        """
        self.lokale_overheid = LokaleOverheid.objects.get(pk=self.kwargs["pk"])
        return self.lokale_overheid

    def get_queryset(self):
        """
        Returns ProductenCatalogus objects for local municipality.
        """
        catalogs = ProductenCatalogus.objects.filter(
            lokale_overheid=self.lokale_overheid
        )

        return (
            super()
            .get_queryset()
            .filter(catalogus__in=catalogs)
            .annotate_name()
            # The `annotate_latest_publication_date` is faster than getting the
            # entire active version with `.active_version`
            .annotate_latest_publication_date()
            .select_related("catalogus__lokale_overheid")
            # FIXME: The proper way is to `.annotate_area` (because it includes)
            # areas for both reference and non-reference products. Alas, this
            # doesn't work well with the datagrid component because it cannot
            # determine that its a FK and list all possible choices.
            # .annotate_area()
            # Instead, we use this line below but it doesn't work for reference
            # products because they don't have reference products themselves.
            .select_related(
                "referentie_product__generiek_product",
                "referentie_product__generiek_product__upn__thema__informatiegebied",
            )
            # FIXME: Similar to above. This doesn't work for reference products.
            .annotate(doelgroep=F("referentie_product__generiek_product__doelgroep"))
            .order_by(
                "_name",
                Case(
                    When(product_aanwezig=True, then=Value(1)),
                    When(product_aanwezig=False, then=Value(2)),
                    When(product_aanwezig=None, then=Value(3)),
                ),
            )
        )
