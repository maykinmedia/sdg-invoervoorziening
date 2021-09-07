from dataclasses import dataclass
from typing import Any


@dataclass
class ProductField:
    name: str
    value: Any
    help_text: str
    is_standard: bool
    is_markdown: bool
