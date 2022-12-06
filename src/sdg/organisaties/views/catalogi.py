import datetime

from django.db.models import F
from django.utils.translation import gettext as _

from rijkshuisstijl.views.generic import ListView as RHListView

from sdg.accounts.mixins import OverheidMixin
from sdg.core.constants.product import DoelgroepChoices
from sdg.core.models import ProductenCatalogus
from sdg.core.views.mixins import SDGSettingsMixin
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.constants import BooleanChoices
from sdg.producten.models import Product


class CatalogListView(
    SDGSettingsMixin,
    OverheidMixin,
    RHListView,
):
    fields = [
        {
            "key": "_name",
            "label": _("Naam"),
            "filter_label": _("Zoek op productnaam"),
        },
        {
            "key": "generiek_product__upn__thema__informatiegebied",
            "label": _("Informatiegebied"),
            "filter_label": _("Selecteer thema"),
        },
        {
            "label": _("Aangeboden"),
            "key": "product_aanwezig",
            "filter_label": " ",
        },
        {
            # FIXME: The relation `generiek_product__doelgroep`
            # doesn't work since doelgroep is not a FK?
            "key": "doelgroep",
            "label": _("Doelgroep"),
            "filter_label": " ",
            "lookup": "doelgroep",
        },
        {
            "label": _("Heeft kosten"),
            "key": "heeft_kosten",
            "filter_label": " ",
        },
        {
            "key": "_latest_publication_date",
            "label": _("Publicatie datum"),
        },
    ]
    filterable_columns = [
        "_name",
        "generiek_product__upn__thema__informatiegebied",
        {
            "key": "product_aanwezig",
            "choices": (("", "---------"),) + BooleanChoices.choices,
        },
        {
            "key": "doelgroep",
            "choices": (("", "---------"),) + DoelgroepChoices.choices,
        },
        {
            "key": "heeft_kosten",
            "choices": (("", "---------"),) + BooleanChoices.choices,
        },
    ]
    # FIXME: Setting orderable columns seems to break ordering entirely.
    # orderable_columns = [
    #     "_name",
    #     "_area",
    #     "pub_date",
    # ]

    model = Product
    template_name = "organisaties/catalogi/list.html"
    paginate_by = 100

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
            .select_related(
                "catalogus__lokale_overheid",
                "generiek_product",
                "generiek_product__upn__thema__informatiegebied",
            )
            # FIXME: We have to annotate doelgroep to fix the RHS-component.
            .annotate(doelgroep=F("generiek_product__doelgroep"))
            .exclude(generiek_product__eind_datum__lte=datetime.date.today())
            .exclude_generic_status()
            .order_by("_name")
        )
