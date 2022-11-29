from dataclasses import dataclass
from typing import Any, List, Optional

from sdg.core.types import LabeledTooltip

FLAG_MAPPING = {"en": "gb"}


def _code_to_flag(country_code):
    return FLAG_MAPPING.get(country_code, country_code)


@dataclass
class ProductFieldMetadata:
    name: str
    verbose_name: str
    value: Any
    help_text: str
    type: str
    configuration: Optional[LabeledTooltip] = None

    def __str__(self):
        return self.value

    def __getattr__(self, name):
        """Allow using is_<x> syntax for field type checking."""
        if name.startswith("is_"):
            return name[3:].lower() in self.type.lower()


@dataclass
class Language:
    name: str
    code: str
    checked: bool
    flag: str = None

    def __post_init__(self):
        self.flag = _code_to_flag(self.code)

    def __str__(self):
        return self.name

    __repr__ = __str__
