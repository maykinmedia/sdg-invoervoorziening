from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ProductFieldInfo:
    name: str
    verbose_name: str
    value: Any
    help_text: str
    type: str
    configuration: Optional[List[str]] = None

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

    _code_to_flag = {"en": "gb"}

    def __post_init__(self):
        self.flag = self._code_to_flag.get(self.code, self.code)

    def __str__(self):
        return self.name

    __repr__ = __str__
