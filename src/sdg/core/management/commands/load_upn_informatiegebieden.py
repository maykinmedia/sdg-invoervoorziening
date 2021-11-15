from sdg.core.management.parsers import ParserCommand
from sdg.core.management.utils import load_upn_informatiegebieden


class Command(ParserCommand):
    plural_object_name = "upn informatiegebieden"

    def handle(self, **options):
        super().handle(load_upn_informatiegebieden, **options)
