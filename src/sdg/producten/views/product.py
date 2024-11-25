import datetime
from itertools import chain, zip_longest
from typing import Tuple

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.template.defaultfilters import capfirst
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import OverheidMixin
from sdg.accounts.models import Role
from sdg.accounts.utils import user_has_valid_roles
from sdg.accounts.views.decorators import municipality_role_required
from sdg.core.constants import TaalChoices
from sdg.core.constants.product import DoelgroepChoices
from sdg.core.types import Event
from sdg.core.views.mixins import BreadcrumbsMixin
from sdg.producten.forms import LocalizedProductFormSet, ProductForm, VersionForm
from sdg.producten.models import Product, ProductVersie
from sdg.producten.models.product import GeneriekProduct
from sdg.producten.utils import (
    build_url_kwargs,
    duplicate_localized_products,
    parse_changed_data,
)
from sdg.utils.validators import validate_placeholders


class ProductPreviewView(OverheidMixin, DetailView):
    """
    Preview a product.

    This view is used to produce a preview example as it is
    used in the municipality website.
    """

    template_name = "mocks/kvk.html"
    context_object_name = "product"
    pk_url_kwarg = "product_pk"
    required_roles = [Role.choices.MANAGER, Role.choices.EDITOR]

    def is_concept(self):
        if self.request.GET.get("status", "") == "concept":
            return True

        return False

    def get_queryset(self):
        if self.is_concept():
            return (
                Product.objects.select_related("catalogus__lokale_overheid")
                .prefetch_related(
                    "locaties",
                    Prefetch(
                        "referentie_product", queryset=Product.objects.most_recent()
                    ),
                )
                .exclude(generiek_product__eind_datum__lte=datetime.date.today())
                .most_recent()
                .active()
            )
        else:
            return (
                Product.objects.select_related("catalogus__lokale_overheid")
                .prefetch_related(
                    "locaties",
                    Prefetch("referentie_product", queryset=Product.objects.active()),
                )
                .exclude(generiek_product__eind_datum__lte=datetime.date.today())
                .active()
            )

    def get_lokale_overheid(self):
        self.object = self.get_object()

        if self.is_concept():
            self.lokale_overheid = (
                self.object.most_recent_version.product.catalogus.lokale_overheid
            )
        else:
            self.lokale_overheid = (
                self.object.active_version.product.catalogus.lokale_overheid
            )

        self.lokale_overheid = self.object.catalogus.lokale_overheid

        return self.lokale_overheid

    def _get_generieke_taal_producten(self):
        required_fields = ["verwijzing_links", "datum_check"]

        nl = self.object.generiek_product.vertalingen.filter(taal="nl").first()
        en = self.object.generiek_product.vertalingen.filter(taal="en").first()

        if nl:
            setattr(nl, "template_fields", nl.get_fields(required_fields))

        if en:
            setattr(en, "template_fields", en.get_fields(required_fields))

        return [nl, en]

    def _get_algemene_taal_producten(self):
        required_fields = [
            "product_aanwezig_toelichting",
            "product_valt_onder_toelichting",
        ]
        if self.is_concept():
            nl = self.object.most_recent_version.vertalingen.filter(taal="nl").first()
            en = self.object.most_recent_version.vertalingen.filter(taal="en").first()
        else:
            nl = self.object.active_version.vertalingen.filter(taal="nl").first()
            en = self.object.active_version.vertalingen.filter(taal="en").first()

        if nl:
            setattr(nl, "template_fields", nl.get_fields(required_fields))

        if en:
            setattr(en, "template_fields", en.get_fields(required_fields))

        return [nl, en]

    def _get_specifieke_taal_producten(self):
        required_fields = [
            "vereisten",
            "bewijs",
            "procedure_beschrijving",
            "kosten_en_betaalmethoden",
            "uiterste_termijn",
            "bezwaar_en_beroep",
            "wtd_bij_geen_reactie",
        ]

        if self.is_concept():
            nl = self.object.most_recent_version.vertalingen.filter(taal="nl").first()
            en = self.object.most_recent_version.vertalingen.filter(taal="en").first()
        else:
            nl = self.object.active_version.vertalingen.filter(taal="nl").first()
            en = self.object.active_version.vertalingen.filter(taal="en").first()

        if nl:
            setattr(nl, "template_fields", nl.get_fields(required_fields))

        if en:
            setattr(en, "template_fields", en.get_fields(required_fields))

        return [nl, en]

    def _get_decentrale_procedure_link(self):
        required_fields = [
            "decentrale_procedure_label",
            "decentrale_procedure_link",
        ]

        if self.is_concept():
            nl = self.object.most_recent_version.vertalingen.filter(taal="nl").first()
            en = self.object.most_recent_version.vertalingen.filter(taal="en").first()
        else:
            nl = self.object.active_version.vertalingen.filter(taal="nl").first()
            en = self.object.active_version.vertalingen.filter(taal="en").first()

        if nl:
            setattr(
                nl,
                "template_fields",
                {field: nl._get_field(field) for field in required_fields},
            )

        if en:
            setattr(
                en,
                "template_fields",
                {field: en._get_field(field) for field in required_fields},
            )

        return [nl, en]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["languages"] = list(TaalChoices.labels.keys())
        context["product"] = self.object
        context["locale_overheid"] = self.object.catalogus.lokale_overheid

        context["product_locaties"] = self.object.locaties.all()

        context["generieke_producten"] = self._get_generieke_taal_producten()
        context["algemene_producten"] = self._get_algemene_taal_producten()
        context["specifieke_producten"] = self._get_specifieke_taal_producten()
        context["decentrale_procedure"] = self._get_decentrale_procedure_link()

        context["days"] = [
            "maandag",
            "dinsdag",
            "woensdag",
            "donderdag",
            "vrijdag",
            "zaterdag",
            "zondag",
        ]

        return context


class ProductUpdateView(
    BreadcrumbsMixin,
    OverheidMixin,
    UpdateView,
):
    """
    Update a product.
    This view is used for both specific product and concept products.
    """

    template_name = "producten/update.html"
    context_object_name = "product_versie"
    pk_url_kwarg = "product_pk"
    form_class = LocalizedProductFormSet

    def get_queryset(self):
        return (
            Product.objects.most_recent()
            .exclude(generiek_product__eind_datum__lte=datetime.date.today())
            .active()
            .select_related(
                "catalogus__lokale_overheid",
                "generiek_product__upn",
            )
            .prefetch_related(
                "generiek_product__vertalingen",
            )
            .exclude_generic_status()
            .annotate_name()
        )

    def get_breadcrumbs_title(self):
        name = capfirst(self.product)

        if self.product.is_referentie_product:
            return f"{name} (referentie)"

        return name

    def get_lokale_overheid(self):
        self.product = self.get_object()
        self.lokale_overheid = self.product.catalogus.lokale_overheid
        self.object = self.product.most_recent_version
        self.product_nl, self.product_en = self.object.vertalingen.all()
        return self.lokale_overheid

    def _save_version_form(
        self, product_form, version_form, localized_formset
    ) -> Tuple[ProductVersie, bool]:
        """
        Save the version form.
        Return a tuple of (version object, created), where created is a boolean
        specifying whether an object was created.
        """
        new_version = version_form.save(commit=False)

        created = self.object != new_version
        new_version.product = self.product
        new_version.gemaakt_door = self.request.user
        new_version.versie = self.object.versie + 1 if created else self.object.versie
        changes_specific_fields = [
            field
            for field in product_form.changed_data
            if field in settings.SDG_LOCALIZED_FORM_FIELDS
        ]
        new_version.bewerkte_velden = list(
            chain.from_iterable(
                [
                    localized_formset.changed_data_localized,
                    parse_changed_data(changes_specific_fields, form=product_form),
                ]
            )
        )
        new_version.save()
        return new_version, created

    def _get_generieke_taal_producten(self):
        required_fields = [
            "product_titel",
            "generieke_tekst",
            "datum_check",
            "verwijzing_links",
        ]
        nl, en = self.product.generiek_product.vertalingen.all()

        if nl:
            setattr(nl, "template_fields", nl.get_fields(required_fields))

        if en:
            setattr(en, "template_fields", en.get_fields(required_fields))

        return [nl, en]

    def _get_published_taal_product_links(self):
        doelgroep = self.product.generiek_product.doelgroep
        if not doelgroep:
            return None

        product_language_urls = (
            self.product.generiek_product.vertalingen.all().values_list(
                "taal", "landelijke_link"
            )
        )
        if not product_language_urls:
            return None

        urls = {}
        for language, product_url in product_language_urls:
            if doelgroep == DoelgroepChoices.bedrijf:
                dop = self.product.catalogus.lokale_overheid.organisatie.dop_slug
                if language == TaalChoices.nl:
                    urls[language] = settings.SDG_DOP_URL_TEMPLATE_NL.format(
                        product_url=product_url, organisation=dop
                    )
                elif language == TaalChoices.en:
                    urls[language] = settings.SDG_DOP_URL_TEMPLATE_EN.format(
                        product_url=product_url, organisation=dop
                    )
            elif doelgroep == DoelgroepChoices.burger:
                dpc = self.product.catalogus.lokale_overheid.organisatie.dpc_slug
                if language == TaalChoices.nl:
                    urls[language] = settings.SDG_DPC_URL_TEMPLATE_NL.format(
                        product_url=product_url, organisation=dpc
                    )
                elif language == TaalChoices.en:
                    urls[language] = settings.SDG_DPC_URL_TEMPLATE_EN.format(
                        product_url=product_url, organisation=dpc
                    )

        return urls

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        generic_information = self.product.generiek_product.vertalingen.all()

        context["generic_products"] = self._get_generieke_taal_producten()

        context["button_information"] = _(
            "'Opslaan als concept' slaat het product op zonder te publiceren zodat u er later nog aan kan werken.\n'Opslaan en publiceren' maakt een nieuwe gepubliceerde versie van het product aan, actief vanaf de gekozen datum aan de linkerkant."
        )

        context["languages"] = list(TaalChoices.labels.keys())
        context["product"] = self.product
        context["doelgroep"] = {
            "value": self.product.generiek_product.doelgroep,
            "help_text": GeneriekProduct._meta.get_field("doelgroep").help_text,
        }
        context["lokaleoverheid"] = self.product.catalogus.lokale_overheid

        context["formset"] = context["form"]
        context["informatie_forms"] = zip_longest(
            generic_information, context["form"].forms
        )

        context["version_form"] = kwargs.get(
            "version_form",
            VersionForm(instance=self.object, product_instance=self.product),
        )
        context["product_form"] = kwargs.get(
            "product_form", ProductForm(instance=self.product)
        )
        context["reference_formset"] = self.form_class(
            product_form=context["product_form"],
            instance=self.product.reference_product.most_recent_version,
        )
        context["previous_reference_formset"] = self.form_class(
            product_form=context["product_form"],
            instance=self.product.reference_product.get_latest_versions(2)[
                -1
            ],  # TODO: optimize
        )

        context["published_product_language_links"] = (
            self._get_published_taal_product_links()
        )

        context["history"] = (
            self.product.get_all_versions()
            | self.product.reference_product.get_all_versions()
        )

        context["areas"] = self.product.get_areas()

        # removing label + link field from the localized_form_fields, because we render them seperately
        localized_form_fields = [
            field
            for field in settings.SDG_LOCALIZED_FORM_FIELDS
            if field not in ["decentrale_procedure_label", "decentrale_procedure_link"]
        ]

        context["localized_form_fields"] = localized_form_fields

        context["user_can_edit"] = user_has_valid_roles(
            self.request.user,
            municipality=self.get_lokale_overheid(),
            required_roles=[
                Role.choices.MANAGER,
                Role.choices.EDITOR,
            ],
        )
        return context

    def _add_placeholder_warning(self):
        """
        Check for any placeholder texts in the current data.
        Add a warning if any are found.
        """
        current_data = chain(
            self.object.__dict__.values(),
            self.product.__dict__.values(),
            self.product_en.__dict__.values(),
            self.product_nl.__dict__.values(),
        )

        for value in current_data:
            if validate_placeholders(value):
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    _("De huidige gegevens bevatten placeholder tekst."),
                )
                return

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data()

        if not self.product.is_referentie_product:
            self._add_placeholder_warning()

        return self.render_to_response(ctx)

    @municipality_role_required([Role.choices.MANAGER, Role.choices.EDITOR])
    def post(self, request, *args, **kwargs):
        product_form = ProductForm(request.POST, instance=self.product)
        version_form = VersionForm(
            request.POST, instance=self.object, product_instance=self.product
        )
        localized_formset = self.form_class(
            request.POST,
            instance=self.object,
            product_form=product_form,
        )

        forms = (product_form, version_form, localized_formset)
        forms_valid = [f.is_valid() for f in forms]
        if not all(forms_valid):
            return self.form_invalid(*forms)

        return self.form_valid(*forms)

    @transaction.atomic
    def form_valid(self, product_form, version_form, localized_formset):
        product_form.save()
        new_version, created = self._save_version_form(
            product_form, version_form, localized_formset
        )

        if created:
            Event.create_and_log(self.request, self.object, Event.CREATE)
            duplicate_localized_products(localized_formset, new_version)
        else:
            Event.create_and_log(self.request, self.object, Event.UPDATE)
            localized_formset.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            _("Product {product} is opgeslagen.").format(product=self.product),
        )

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, product_form, version_form, localized_formset):
        context = self.get_context_data(
            form=localized_formset,
            version_form=version_form,
            product_form=product_form,
        )

        messages.add_message(
            self.request,
            messages.ERROR,
            _(
                "Wijzigingen konden niet worden opgeslagen. Corrigeer de hieronder gemarkeerde fouten."
            ),
        )

        return self.render_to_response(context)

    def get_success_url(self):
        return reverse(
            "organisaties:catalogi:producten:edit",
            kwargs=build_url_kwargs(self.product),
        )
