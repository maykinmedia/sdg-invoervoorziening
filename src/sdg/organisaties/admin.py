from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.utils.translation import ugettext_lazy as _

from sdg.accounts.models import Role
from sdg.core.admin.mixins import BaseProductFilter
from sdg.organisaties.models import LokaleOverheid, Lokatie as Locatie


class LocatieInline(admin.StackedInline):
    model = Locatie
    extra = 0


class HasManagerProductFilter(BaseProductFilter):
    title = _("Beheerder")
    parameter_name = "beheerder"
    filter_field = "_has_manager"


@admin.register(LokaleOverheid)
class LokaleOverheidAdmin(admin.ModelAdmin):
    model = LokaleOverheid

    list_display = ("organisatie", "has_manager", "contact_website", "contact_naam")
    list_filter = (HasManagerProductFilter,)
    ordering = ("organisatie__owms_pref_label",)
    search_fields = (
        "organisatie__owms_pref_label",
        "contact_naam",
        "contact_emailadres",
        "contact_website",
    )
    inlines = (LocatieInline,)
    autocomplete_fields = (
        "organisatie",
        "ondersteunings_organisatie",
        "verantwoordelijke_organisatie",
        "bevoegde_organisatie",
    )

    def get_queryset(self, request):
        """Annotate municipalities with a boolean indicating if contains managers."""
        queryset = super().get_queryset(request)
        manager_role = Role.objects.filter(
            is_beheerder=True, lokale_overheid=OuterRef("pk")
        )
        queryset = queryset.annotate(_has_manager=Exists(manager_role))
        return queryset

    def has_manager(self, obj):
        """:returns: Annotated boolean for list display purposes."""
        return obj._has_manager

    has_manager.short_description = _("beheerder")
    has_manager.boolean = True
    has_manager.admin_order_field = "_has_manager"


@admin.register(Locatie)
class LocatieAdmin(admin.ModelAdmin):
    model = Locatie
    autocomplete_fields = ("lokale_overheid",)
