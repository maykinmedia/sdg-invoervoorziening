from django.http import HttpResponseRedirect
from django.views.generic import DetailView, UpdateView

from sdg.accounts.mixins import OverheidRoleRequiredMixin
from sdg.core.models import ProductenCatalogus, Thema
from sdg.organisaties.forms import LokaleOverheidForm, LokatieInlineFormSet
from sdg.organisaties.models import LokaleOverheid
from sdg.producten.models import Product


class LokaleOverheidDetailView(OverheidRoleRequiredMixin, DetailView):
    template_name = "organisaties/overheid_detail.html"
    model = LokaleOverheid
    required_roles = ["is_beheerder", "is_redacteur"]

    def get_lokale_overheid(self):
        self.object = self.get_object()
        return self.object

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        self.object.create_specific_catalogs()

        # TODO: Optimize / refactor [.->L63]
        theme_list = (
            Thema.objects.all()
            .select_related("informatiegebied")
            .prefetch_related("upn")
        )
        area_and_products = {
            theme.informatiegebied.informatiegebied: [] for theme in theme_list
        }
        catalogs = []
        for role in self.request.user.roles.filter(
            is_redacteur=True, lokale_overheid=self.object
        ):
            for catalog in role.get_catalogs():
                catalog_area_and_products = area_and_products.copy()
                for theme in theme_list:
                    theme_upns = theme.upn.all()
                    if theme_upns:
                        specific_products = Product.objects.filter(
                            referentie_product__generiek_product__upn__in=theme_upns,
                            catalogus=catalog,
                        )
                        specific_upns = specific_products.values(
                            "referentie_product__generiek_product__upn"
                        )
                        reference_products = Product.objects.filter(
                            generiek_product__upn__in=theme_upns,
                            catalogus=catalog.referentie_catalogus,
                        ).exclude(generiek_product__upn__in=specific_upns)
                        catalog_area_and_products[
                            theme.informatiegebied.informatiegebied
                        ].extend(specific_products | reference_products)
                setattr(catalog, "area_and_products", catalog_area_and_products)
                catalogs.append(catalog)
        context["catalogs"] = catalogs

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related("lokaties", "organisatie", "catalogi")


class LokaleOverheidUpdateView(OverheidRoleRequiredMixin, UpdateView):
    template_name = "organisaties/overheid_update.html"
    form_class = LokaleOverheidForm
    model = LokaleOverheid
    required_roles = ["is_beheerder", "is_redacteur"]

    def get_lokale_overheid(self):
        self.object = self.get_object()
        return self.object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["formset"] = kwargs.get("formset") or LokatieInlineFormSet(
            instance=self.object, prefix="form"
        )
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.object)
        formset = LokatieInlineFormSet(
            request.POST, instance=self.object, prefix="form"
        )

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset=formset)
        else:
            return self.form_invalid(form, formset=formset)

    def form_valid(self, form, formset=None):
        self.object = form.save()
        if formset:
            formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset=None):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )
