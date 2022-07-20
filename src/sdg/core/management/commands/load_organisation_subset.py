from sdg.core.management.parsers import ParserCommand
from sdg.core.management.utils import load_organisation_subset


class Command(ParserCommand):
    plural_object_name = "organisations"
    xml_column_names = [
        "prefLabel",
        "resourceIdentifier",
        "endDate",
    ]

    def handle(self, **options):
        super().handle(load_organisation_subset, **options)
