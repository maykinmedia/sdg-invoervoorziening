from datetime import datetime

from django.test import TestCase

import requests_mock
from freezegun import freeze_time

from sdg.core.constants import TaalChoices

from ...core.models import LocalizedProductFieldConfiguration, ProductFieldConfiguration
from ..broken_links import check_broken_links, get_product_urls, reset_broken_links
from ..models import BrokenLinks, Product
from .constants import FUTURE_DATE, NOW_DATE
from .factories.localized import LocalizedProductFactory
from .factories.product import (
    BrokenLinksFactory,
    GeneriekProductFactory,
    ProductVersieFactory,
    SpecifiekProductFactory,
)


@freeze_time(NOW_DATE)
class GetProductUrlsTestCase(TestCase):
    def test_get_product_urls_with_valid_urls(self):
        assert Product.objects.count() == 0
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
            verwijzing_links=[
                ["label1", "https://example.com/verwijzing_links/1"],
                ["label2", "https://example.com/verwijzing_links/2"],
            ],
            decentrale_procedure_label="label",
            decentrale_procedure_link="https://example.com/product/decentrale_procedure_link",
        )

        products = Product.objects.prefetch_related(
            "most_recent_version__vertalingen"
        ).exclude_generic_status()
        product_urls = get_product_urls(products)

        # specifieke_tekst
        self.assertIn(
            {
                "field": f"specifieke_tekst ({TaalChoices.nl})",
                "label": "valid url",
                "url": "https://example.com/specifieke_tekst",
            },
            product_urls[product.pk],
        )
        # verwijzing_links
        self.assertIn(
            {
                "field": f"verwijzing_links ({TaalChoices.nl})",
                "label": "label1",
                "url": "https://example.com/verwijzing_links/1",
            },
            product_urls[product.pk],
        )
        self.assertIn(
            {
                "field": f"verwijzing_links ({TaalChoices.nl})",
                "label": "label2",
                "url": "https://example.com/verwijzing_links/2",
            },
            product_urls[product.pk],
        )
        # decentrale_procedure_link
        self.assertIn(
            {
                "field": f"decentrale_procedure_link ({TaalChoices.nl})",
                "label": "label",
                "url": "https://example.com/product/decentrale_procedure_link",
            },
            product_urls[product.pk],
        )

    def test_get_product_urls_with_global_config_fields(self):
        localized_config = LocalizedProductFieldConfiguration.objects.get(
            taal=TaalChoices.nl
        )
        localized_config.localizedproduct_specifieke_tekst = [
            ["specifieke_tekst (verandered)", ""]
        ]
        localized_config.localizedproduct_verwijzing_links = [
            ["verwijzing_links (verandered)", ""]
        ]
        localized_config.localizedproduct_decentrale_procedure_link = [
            ["decentrale_procedure_link (verandered)", ""]
        ]
        localized_config.save()

        assert Product.objects.count() == 0
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
            verwijzing_links=[
                ["label1", "https://example.com/verwijzing_links/1"],
                ["label2", "https://example.com/verwijzing_links/2"],
            ],
            decentrale_procedure_label="label",
            decentrale_procedure_link="https://example.com/product/decentrale_procedure_link",
        )

        products = Product.objects.prefetch_related(
            "most_recent_version__vertalingen"
        ).exclude_generic_status()
        product_urls = get_product_urls(products)

        # specifieke_tekst
        self.assertIn(
            {
                "field": f"specifieke_tekst (verandered) ({TaalChoices.nl})",
                "label": "valid url",
                "url": "https://example.com/specifieke_tekst",
            },
            product_urls[product.pk],
        )
        # verwijzing_links
        self.assertIn(
            {
                "field": f"verwijzing_links (verandered) ({TaalChoices.nl})",
                "label": "label1",
                "url": "https://example.com/verwijzing_links/1",
            },
            product_urls[product.pk],
        )
        self.assertIn(
            {
                "field": f"verwijzing_links (verandered) ({TaalChoices.nl})",
                "label": "label2",
                "url": "https://example.com/verwijzing_links/2",
            },
            product_urls[product.pk],
        )
        # decentrale_procedure_link
        self.assertIn(
            {
                "field": f"decentrale_procedure_link (verandered) ({TaalChoices.nl})",
                "label": "label",
                "url": "https://example.com/product/decentrale_procedure_link",
            },
            product_urls[product.pk],
        )

        # cleanup
        localized_config.localizedproduct_specifieke_tekst = []
        localized_config.localizedproduct_verwijzing_links = []
        localized_config.localizedproduct_decentrale_procedure_link = []
        localized_config.save()
        ProductFieldConfiguration.clear_cache()

    def test_invalide_urls_return_nothing(self):
        assert Product.objects.count() == 0
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
            # not a valid ckeditor altered link
            bewijs="https://example.com/korte_omschrijving",
            bezwaar_en_beroep="",
            verwijzing_links=[
                ["label1", "#https://example.com/fragmented-url"],
                ["label2", "<a href='No url found in this field'>what></a>"],
            ],
            decentrale_procedure_label="label",
            # checks for correct scheme
            decentrale_procedure_link="https:example.",
        )

        products = Product.objects.prefetch_related(
            "most_recent_version__vertalingen"
        ).exclude_generic_status()
        product_urls = get_product_urls(products)
        # specifieke_tekst
        self.assertEqual(product_urls, {})


@requests_mock.Mocker()
class CheckBrokenLinksTestCase(TestCase):
    def test_valid_urls_do_not_create_broken_link_object(self, m):
        assert BrokenLinks.objects.count() == 0
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

        check_broken_links()

        self.assertEqual(BrokenLinks.objects.count(), 0)

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

        check_broken_links()

        broken_link = BrokenLinks.objects.get()
        self.assertEqual(broken_link.product, product)
        self.assertEqual(
            broken_link.occurring_field, f"specifieke_tekst ({TaalChoices.nl})"
        )
        self.assertEqual(broken_link.url, "https://example.com/specifieke_tekst")
        self.assertEqual(broken_link.url_label, "valid url")
        self.assertEqual(broken_link.error_count, 1)

    @freeze_time(FUTURE_DATE)
    def test_broken_link_increase_number_when_still_present(self, m):
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
        broken_link = BrokenLinksFactory.create(
            product=product,
            url="https://example.com/specifieke_tekst",
            last_checked=NOW_DATE,
            occurring_field=f"specifieke_tekst ({TaalChoices.nl})",
            url_label="valid url",
            error_count=1,
        )

        check_broken_links()

        broken_link.refresh_from_db()
        self.assertEqual(broken_link.last_checked, datetime(3000, 1, 1, 0, 0))
        self.assertEqual(broken_link.error_count, 2)

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

        check_broken_links()

        self.assertFalse(BrokenLinks.objects.filter(pk=broken_link.pk).exists())


class ResetBrokenLinksTestCase(TestCase):
    def test_reset_links(self):
        assert BrokenLinks.objects.count() == 0
        generiek_product = GeneriekProductFactory.create()
        product = SpecifiekProductFactory.create(
            referentie_product=None, generiek_product=generiek_product
        )
        BrokenLinksFactory.create_batch(3, product=product, error_count=5)

        reset_broken_links(reset_all=True)

        for broken_link in BrokenLinks.objects.all():
            self.assertEqual(broken_link.error_count, 0)

    def test_delete_links(self):
        generiek_product = GeneriekProductFactory.create()
        product = SpecifiekProductFactory.create(
            referentie_product=None, generiek_product=generiek_product
        )
        BrokenLinksFactory.create_batch(3, product=product)

        reset_broken_links()

        self.assertEqual(BrokenLinks.objects.count(), 0)

    def test_delete_links_except_provided_broken_links_to_ignore(self):
        assert BrokenLinks.objects.count() == 0
        generiek_product = GeneriekProductFactory.create()
        product = SpecifiekProductFactory.create(
            referentie_product=None, generiek_product=generiek_product
        )
        link1, link2, link3 = BrokenLinksFactory.create_batch(3, product=product)

        reset_broken_links(ignore_broken_ids=[link1.pk, link2.pk])

        self.assertEqual(BrokenLinks.objects.count(), 2)
        self.assertFalse(BrokenLinks.objects.filter(pk=link3.pk).exists())
