import csv
import os
from typing import Any, Dict, List

from django.core.management import BaseCommand, CommandError

from lxml import etree


class ParserException(Exception):
    pass


class OwmsParser:
    available_parsers = {"csv", "xml"}

    def __init__(self, xml_column_names=None):
        self.xml_column_names = xml_column_names

    def parse(self, filename: str):
        """Calls parsing function based on filename extension."""

        _, extension = os.path.splitext(filename)
        file_format = extension[1:]

        if file_format in self.available_parsers:
            return getattr(self, file_format)(filename)
        else:
            raise ParserException("File format does not exist")

    def xml(self, filename: str) -> List[Dict[str, Any]]:
        if not self.xml_column_names:
            raise ParserException("Invalid XML column names")

        tree = etree.parse(filename)
        values = tree.findall("value")
        return [
            {
                column: value.find(column).text
                if value.find(column) is not None
                else None
                for column in self.xml_column_names
            }
            for value in values
        ]

    def csv(self, filename: str) -> List[Dict[str, Any]]:
        with open(filename, encoding="utf-8-sig") as f:
            data = csv.DictReader(f)
            return list(data)


class ParserCommand(BaseCommand):
    plural_object_name = "objects"
    xml_column_names = None

    def __init__(self):
        self.help = (
            f"Load {self.plural_object_name} to the database from a given XML/CSV file."
        )
        self.parser = OwmsParser(xml_column_names=self.xml_column_names)
        super().__init__()

    def add_arguments(self, parser):
        parser.add_argument(
            "filename",
            help="The name of the file to be imported.",
        )

    def handle(self, handler_function, **options):
        filename = options.pop("filename")

        data = self.parse(filename)
        created_count = handler_function(data)

        self.stdout.write(
            self.style.SUCCESS(
                f"Succesfully imported {self.plural_object_name} from {filename} ({created_count} objects)."
            )
        )

    def parse(self, filename) -> List[Dict[str, Any]]:
        try:
            return self.parser.parse(filename)
        except ParserException:
            raise CommandError(
                f"No parser available for that format. Available: {', '.join(self.parser.available_parsers)}"
            )
