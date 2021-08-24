from sdg.core.management.parsers import ParserCommand
from sdg.core.management.utils import load_upn


class Command(ParserCommand):
    plural_object_name = "upn"

    def handle(self, **options):
        super().handle(load_upn, **options)
