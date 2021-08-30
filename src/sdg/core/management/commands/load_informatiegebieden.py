from sdg.core.management.parsers import ParserCommand
from sdg.core.management.utils import load_informatiegebieden


class Command(ParserCommand):
    plural_object_name = "informatiegebieden"

    def handle(self, **options):
        super().handle(load_informatiegebieden, **options)
