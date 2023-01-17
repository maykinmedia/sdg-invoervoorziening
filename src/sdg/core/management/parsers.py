import csv
import logging
import os
from tempfile import NamedTemporaryFile
from typing import Any, Dict, List

from django.core.management import BaseCommand, CommandError

import requests
from lxml import etree

logger = logging.getLogger(__name__)


class ParserException(Exception):
    pass


class OwmsParser:
    available_parsers = {"csv", "xml"}

    def __init__(self, xml_column_names=None):
        self.xml_column_names = xml_column_names

    def parse(self, filename: str):
        """Call parsing function based on filename extension."""

        _, extension = os.path.splitext(filename)
        file_format = extension[1:]

        if not filename.startswith("http"):
            return self.process_file(filename, file_format)

        with NamedTemporaryFile() as f:
            f.write(requests.get(filename).content)
            f.seek(0)
            return self.process_file(f.name, file_format)

    def process_file(self, filename, file_format):
        """Process a given file, calling a specific method based on the given format."""
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
                column: getattr(value.find(column), "text", None)
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

        self.stdout.write(f"Importing {self.plural_object_name} from {filename}...")

        try:
            data = self.parse(filename)
            created_count = handler_function(data)
        except Exception as e:
            self.stderr.write(f"Error: {e}")
            logger.exception(e)
        else:
            self.stdout.write(self.style.SUCCESS(f"Done ({created_count} objects)."))

    def parse(self, filename) -> List[Dict[str, Any]]:
        try:
            return self.parser.parse(filename)
        except ParserException:
            raise CommandError(
                f"No parser available for that format. Available: {', '.join(self.parser.available_parsers)}"
            )
