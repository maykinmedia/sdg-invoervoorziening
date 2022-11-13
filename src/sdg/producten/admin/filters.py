from itertools import chain

from django.contrib import admin
from django.utils.translation import gettext_lazy as _


class IsSDGProductFilter(admin.SimpleListFilter):
    title = _("is SDG product")
    parameter_name = "is_sdg_product"
    filter_field = "upn__sdg"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Ja"),
            ("no", "Nee"),
        )

    def queryset(self, request, queryset):
        if self.value() in chain.from_iterable(self.lookup_choices):
            if self.value() == "yes":
                return queryset.filter(upn__sdg__len__gt=0)
            elif self.value() == "no":
                return queryset.filter(upn__sdg__len=0)
        return queryset
