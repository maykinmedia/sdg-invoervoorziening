from abc import ABC
from itertools import chain

from django.contrib import admin


class BaseProductFilter(admin.SimpleListFilter, ABC):
    title = None
    parameter_name = None
    filter_field = None

    def lookups(self, request, model_admin):
        return (
            ("Ja", "Ja"),
            ("Nee", "Nee"),
        )

    def queryset(self, request, queryset):
        if self.value() in chain.from_iterable(self.lookup_choices):
            filter_bool = bool(self.value() == "Ja")
            return queryset.filter(**{self.filter_field: filter_bool})
        return queryset
