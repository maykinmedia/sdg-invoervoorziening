from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.utils.translation import gettext_lazy as _

from sdg.accounts.models import Role
from sdg.core.admin.mixins import BaseProductFilter
from sdg.organisaties.models import (
    BevoegdeOrganisatie,
    LokaleOverheid,
    Lokatie as Locatie,
)


class LocatieInline(admin.StackedInline):
    model = Locatie
    extra = 0


class BevoegdeOrganisatieInline(admin.StackedInline):
    model = BevoegdeOrganisatie
    extra = 0
    autocomplete_fields = ("organisatie",)


class HasManagerProductFilter(BaseProductFilter):
    title = _("Beheerder")
    parameter_name = "beheerder"
    filter_field = "_has_manager"


@admin.register(BevoegdeOrganisatie)
class BevoegdeOrganisatieAdmin(admin.ModelAdmin):
    search_fields = ("naam",)


@admin.register(LokaleOverheid)
class LokaleOverheidAdmin(admin.ModelAdmin):
    list_display = (
        "organisatie",
        "managers",
        "contact_website",
        "owms_end_date",
    )
    list_filter = (HasManagerProductFilter, "organisatie__owms_end_date")
    ordering = ("organisatie__owms_pref_label",)
    search_fields = (
        "organisatie__owms_pref_label",
        "contact_emailadres",
        "contact_website",
    )
    inlines = (LocatieInline, BevoegdeOrganisatieInline)
    autocomplete_fields = (
        "organisatie",
        "ondersteunings_organisatie",
    )

    def get_queryset(self, request):
        """Annotate municipalities with a boolean indicating if contains managers."""
        queryset = super().get_queryset(request)
        manager_role = Role.objects.filter(
            is_beheerder=True, lokale_overheid=OuterRef("pk")
        )
        queryset = (
            queryset.annotate(_has_manager=Exists(manager_role))
            .select_related("organisatie")
            .prefetch_related("roles")
        )
        return queryset

    def managers(self, obj):
        """:returns: Annotated boolean for list display purposes."""
        return ", ".join(
            [str(role.user) for role in obj.roles.all() if role.is_beheerder]
        )

    managers.short_description = _("beheerders")

    def owms_end_date(self, obj):
        return obj.organisatie.owms_end_date

    owms_end_date.short_description = _("end date")
    owms_end_date.admin_order_field = "organisatie__owms_end_date"


@admin.register(Locatie)
class LocatieAdmin(admin.ModelAdmin):
    model = Locatie
    autocomplete_fields = ("lokale_overheid",)
    search_fields = ("naam",)
