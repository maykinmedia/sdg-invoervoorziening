from io import StringIO

from django.core.management import call_command
from django.test import TestCase

import requests_mock

from ...core.constants import TaalChoices
from ..models import BrokenLinks
from .constants import FUTURE_DATE, NOW_DATE
from .factories.localized import LocalizedProductFactory
from .factories.product import (
    BrokenLinksFactory,
    GeneriekProductFactory,
    ProductVersieFactory,
    SpecifiekProductFactory,
)


class TestCheckBrokenLinksCommandTestCase(TestCase):
    def call_command(self, command_name, *args, **kwargs):
        out = StringIO()
        call_command(
            command_name,
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_handle_response_code_successful(self):
        out = self.call_command("check_broken_links")
        self.assertIn("Deleted 0 old BrokenLink(s).", out)

    def test_reset_all_broken_links(self):
        out = self.call_command("check_broken_links", "--reset")
        self.assertIn(
            "Successfully cleared the error_count of every BrokenLink.", str(out)
        )

    @requests_mock.Mocker()
    def test_create_broken_link_object(self, m):
        assert BrokenLinks.objects.count() == 0
        m.register_uri(requests_mock.ANY, requests_mock.ANY, status_code=404)

        generiek_product = GeneriekProductFactory.create()
        product = SpecifiekProductFactory.create(
            referentie_product=None, generiek_product=generiek_product
        )
        product_versie = ProductVersieFactory.create(
            product=product,
            publicatie_datum=FUTURE_DATE,
            versie=1,
        )
        LocalizedProductFactory.create(
            taal=TaalChoices.nl,
            product_versie=product_versie,
            specifieke_tekst="Dummy text with a <a href='https://example.com/specifieke_tekst'>valid url</a>.",
            verwijzing_links=[],
            decentrale_procedure_label="",
            decentrale_procedure_link="",
        )

        out = self.call_command("check_broken_links")

        self.assertIn("Deleted 0 old BrokenLink(s).", str(out))
        broken_link = BrokenLinks.objects.get()
        self.assertEqual(broken_link.product, product)
        self.assertEqual(
            broken_link.occurring_field, f"specifieke_tekst ({TaalChoices.nl})"
        )
        self.assertEqual(broken_link.url, "https://example.com/specifieke_tekst")
        self.assertEqual(broken_link.url_label, "valid url")
        self.assertEqual(broken_link.error_count, 1)

    @requests_mock.Mocker()
    def test_remove_broken_link_when_url_is_valid(self, m):
        m.register_uri(requests_mock.ANY, requests_mock.ANY, status_code=200)

        generiek_product = GeneriekProductFactory.create()
        product = SpecifiekProductFactory.create(
            referentie_product=None, generiek_product=generiek_product
        )
        product_versie = ProductVersieFactory.create(
            product=product,
            publicatie_datum=FUTURE_DATE,
            versie=1,
        )
        LocalizedProductFactory.create(
            taal=TaalChoices.nl,
            product_versie=product_versie,
            specifieke_tekst="Dummy text with a <a href='https://example.com/specifieke_tekst'>valid url</a>.",
            verwijzing_links=[],
            decentrale_procedure_label="",
            decentrale_procedure_link="",
        )
        broken_link = BrokenLinksFactory.create(
            product=product,
            url="https://example.com/specifieke_tekst",
            last_checked=NOW_DATE,
            occurring_field=f"specifieke_tekst ({TaalChoices.nl})",
            url_label="valid url",
            error_count=1,
        )

        out = self.call_command("check_broken_links")

        self.assertIn("Deleted 1 old BrokenLink(s).", str(out))
        self.assertFalse(BrokenLinks.objects.filter(pk=broken_link.pk).exists())
