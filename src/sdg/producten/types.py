from dataclasses import dataclass
from typing import Any


@dataclass
class ProductInfo:
    name: str
    verbose_name: str
    value: Any
    help_text: str
    is_markdown: bool
    is_reference: bool
    is_list: bool


@dataclass
class Language:
    name: str
    code: str
    checked: bool
    flag: str = None

    _code_to_flag = {"en": "gb"}

    def __post_init__(self):
        self.flag = self._code_to_flag.get(self.code, self.code)
