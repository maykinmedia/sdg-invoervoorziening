from sdg.core.types import LabeledTooltip
from sdg.core.utils import unpack


class ProductFieldConfigurationMixin:
    def for_field(self, prefix, name, default=None):
        if name != "config":
            if not (value := getattr(self, f"{prefix}_{name}", None)):
                return default

            label, tooltip = unpack(value)
            return LabeledTooltip(label=label, tooltip=tooltip)
