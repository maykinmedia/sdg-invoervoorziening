from datetime import datetime
from unittest import skip

from django.urls import reverse

from django_webtest import WebTest
from freezegun import freeze_time

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.core.models import ProductenCatalogus
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import OverheidsorganisatieFactory
from sdg.organisaties.tests.factories.overheid import (
    LocatieFactory,
    LokaleOverheidFactory,
)
from sdg.producten.tests.factories.localized import (
    LocalizedReferentieProductFactory,
    LocalizedSpecifiekProductFactory,
)
from sdg.producten.tests.factories.product import ReferentieProductFactory

CATALOG_SELECTOR = ".datagrid__body"
PRODUCT_SELECTOR = ".datagrid__row--cells"


class CatalogListViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.app.set_user(self.user)

    def test_unable_to_access_municipality_without_permission(self):
        lokale_overheid = LokaleOverheidFactory.create()
        self.app.get(lokale_overheid.get_absolute_url(), status=403)

    def test_able_to_access_municipality_with_permission(self):
        lokale_overheid = LokaleOverheidFactory.create()
        RoleFactory.create(
            user=self.user,
            lokale_overheid=lokale_overheid,
            is_redacteur=True,
        )
        self.app.get(lokale_overheid.get_absolute_url())

    @freeze_time("Jan 1th, 2021")
    def test_able_to_access_municipality_before_end_date(self):
        lokale_overheid = LokaleOverheidFactory.create()
        RoleFactory.create(
            user=self.user,
            lokale_overheid=lokale_overheid,
            is_redacteur=True,
        )
        lokale_overheid.organisatie.owms_end_date = datetime(day=3, month=1, year=2021)
        lokale_overheid.organisatie.save()
        self.app.get(lokale_overheid.get_absolute_url(), status=200)

    @freeze_time("Jan 5th, 2021")
    def test_unable_to_access_municipality_after_end_date(self):
        lokale_overheid = LokaleOverheidFactory.create()
        RoleFactory.create(
            user=self.user,
            lokale_overheid=lokale_overheid,
            is_redacteur=True,
        )
        lokale_overheid.organisatie.owms_end_date = datetime(day=3, month=1, year=2021)
        lokale_overheid.organisatie.save()
        self.app.get(lokale_overheid.get_absolute_url(), status=403)

    def test_specific_catalog_is_automatically_generated(self):
        localized_reference_product = LocalizedReferentieProductFactory.create()
        reference_catalog = localized_reference_product.product_versie.product.catalogus
        reference_lokale_overheid = reference_catalog.lokale_overheid

        self.assertEqual(ProductenCatalogus.objects.count(), 1)

        RoleFactory.create(
            user=self.user, lokale_overheid=reference_lokale_overheid, is_redacteur=True
        )

        self.app.get(reference_lokale_overheid.get_absolute_url())
        self.assertEqual(ProductenCatalogus.objects.count(), 2)

    def test_specific_catalog_is_not_automatically_generated_if_disabled(self):
        localized_reference_product = LocalizedReferentieProductFactory.create()
        reference_catalog = localized_reference_product.product_versie.product.catalogus
        reference_lokale_overheid = reference_catalog.lokale_overheid
        reference_lokale_overheid.automatisch_catalogus_aanmaken = False
        reference_lokale_overheid.save()

        self.assertEqual(ProductenCatalogus.objects.count(), 1)

        RoleFactory.create(
            user=self.user, lokale_overheid=reference_lokale_overheid, is_redacteur=True
        )

        self.app.get(reference_lokale_overheid.get_absolute_url())
        self.assertEqual(ProductenCatalogus.objects.count(), 1)

    def test_specific_catalog_is_displayed(self):
        localized_reference_product = LocalizedReferentieProductFactory.create()
        reference_product = localized_reference_product.product_versie.product
        reference_catalog = reference_product.catalogus

        localized_product = LocalizedSpecifiekProductFactory.create(
            product_versie__product__referentie_product=reference_product,
            product_versie__product__catalogus__referentie_catalogus=reference_catalog,
        )
        product = localized_product.product_versie.product
        specific_catalog = product.catalogus
        specific_lokale_overheid = specific_catalog.lokale_overheid

        RoleFactory.create(
            user=self.user,
            lokale_overheid=specific_lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(specific_lokale_overheid.get_absolute_url())

        self.assertEqual(response.pyquery(CATALOG_SELECTOR).length, 1)

    @skip("TODO: Clarify if both catalogs must be displayed")
    def test_both_reference_and_specific_catalog_are_displayed(self):
        localized_reference_product = LocalizedReferentieProductFactory.create()
        reference_product = localized_reference_product.product_versie.product
        reference_catalog = reference_product.catalogus
        reference_lokale_overheid = reference_catalog.lokale_overheid

        localized_product = LocalizedSpecifiekProductFactory.create(
            product_versie__product__referentie_product=reference_product,
            product_versie__product__catalogus__referentie_catalogus=reference_catalog,
            product_versie__product__catalogus__lokale_overheid=reference_lokale_overheid,
        )
        product = localized_product.product_versie.product
        specific_catalog = product.catalogus

        RoleFactory.create(
            user=self.user, lokale_overheid=reference_lokale_overheid, is_redacteur=True
        )

        response = self.app.get(reference_lokale_overheid.get_absolute_url())

        response_text = response.text

        self.assertIn(
            reference_catalog.naam,
            response_text,
        )
        self.assertIn(
            specific_catalog.naam,
            response_text,
        )
        self.assertEqual(response.pyquery(CATALOG_SELECTOR).length, 2)

    def test_specific_products_are_displayed(self):
        reference_catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True
        )
        reference_products = ReferentieProductFactory.create_batch(
            3, catalogus=reference_catalog
        )

        specific_catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=False,
            referentie_catalogus=reference_catalog,
        )
        specific_lokale_overheid = specific_catalog.lokale_overheid
        specific_products = []
        for reference_product in reference_products:
            LocalizedReferentieProductFactory.create(
                product_versie__product=reference_product,
                product_versie__product__catalogus=reference_catalog,
            )
            localized_specific_product = LocalizedSpecifiekProductFactory.create(
                product_versie__product__referentie_product=reference_product,
                product_versie__product__catalogus=specific_catalog,
            )
            specific_products.append(localized_specific_product.product_versie.product)

        RoleFactory.create(
            user=self.user,
            lokale_overheid=specific_lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(specific_lokale_overheid.get_absolute_url())

        response_text = response.text.lower()

        self.assertEqual(response.pyquery(CATALOG_SELECTOR).length, 1)
        self.assertEqual(response.pyquery(PRODUCT_SELECTOR).length, 3)
        for product in specific_products:
            self.assertIn(str(product), response_text)

    @skip("TODO: Clarify if both catalogs must be displayed")
    def test_both_reference_and_specific_products_are_displayed(self):
        reference_catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True
        )
        reference_products = ReferentieProductFactory.create_batch(
            3, catalogus=reference_catalog
        )
        reference_lokale_overheid = reference_catalog.lokale_overheid

        specific_catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=False,
            lokale_overheid=reference_lokale_overheid,
            referentie_catalogus=reference_catalog,
        )
        specific_products = []
        for reference_product in reference_products:
            LocalizedReferentieProductFactory.create(
                product_versie__product=reference_product,
                product_versie__product__catalogus=reference_catalog,
            )
            localized_specific_product = LocalizedSpecifiekProductFactory.create(
                product_versie__product__referentie_product=reference_product,
                product_versie__product__catalogus=specific_catalog,
            )
            specific_products.append(localized_specific_product.product_versie.product)

        RoleFactory.create(
            user=self.user, lokale_overheid=reference_lokale_overheid, is_redacteur=True
        )

        response = self.app.get(reference_lokale_overheid.get_absolute_url())

        response_text = response.text.lower()

        self.assertEqual(response.pyquery(CATALOG_SELECTOR).length, 2)
        self.assertEqual(response.pyquery(PRODUCT_SELECTOR).length, 6)
        self.assertIn(
            specific_catalog.naam,
            response_text,
        )
        for product in specific_products:
            self.assertIn(str(product), response_text)


class LokaleOverheidUpdateViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.url = "organisaties:edit"
        self.user = UserFactory.create()
        self.app.set_user(self.user)

        self.lokale_overheid = LokaleOverheidFactory.create()
        RoleFactory.create(
            user=self.user,
            lokale_overheid=self.lokale_overheid,
            is_redacteur=True,
        )

    def test_can_update_municipality_details(self):
        response = self.app.get(
            reverse(self.url, kwargs={"pk": self.lokale_overheid.pk})
        )

        response.form["contact_website"] = "https://example.com"
        response.form["contact_emailadres"] = "email@example.com"
        response.form["contact_telefoonnummer"] = "0619123123"
        response.form.submit()

        self.lokale_overheid.refresh_from_db()
        self.assertEqual(self.lokale_overheid.contact_website, "https://example.com")
        self.assertEqual(self.lokale_overheid.contact_emailadres, "email@example.com")
        self.assertEqual(self.lokale_overheid.contact_telefoonnummer, "0619123123")

    def test_municipality_organization_is_readonly(self):
        org = OverheidsorganisatieFactory.create()
        response = self.app.get(
            reverse(self.url, kwargs={"pk": self.lokale_overheid.pk})
        )

        response.form["contact_website"] = "https://example.com"
        response.form["organisatie"].value = org.pk
        response.form.submit()

        self.lokale_overheid.refresh_from_db()
        self.assertEqual(self.lokale_overheid.contact_website, "https://example.com")
        self.assertNotEqual(self.lokale_overheid.organisatie, org.pk)


class LocatieUpdateViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.url = "organisaties:locaties"
        self.user = UserFactory.create()
        self.app.set_user(self.user)

        self.lokale_overheid = LokaleOverheidFactory.create()
        RoleFactory.create(
            user=self.user,
            lokale_overheid=self.lokale_overheid,
            is_redacteur=True,
        )

    def test_can_update_municipality_location(self):
        LocatieFactory.create(lokale_overheid=self.lokale_overheid)

        response = self.app.get(
            reverse(self.url, kwargs={"pk": self.lokale_overheid.pk})
        )

        response.form["form-0-naam"] = "Name"
        response.form["form-0-straat"] = "Street"
        response.form["form-0-nummer"] = 91
        response.form["form-0-plaats"] = "Town"
        response.form["form-0-postcode"] = "1234AB"
        response.form["form-0-land"] = "Country"
        response.form.submit()

        self.lokale_overheid.refresh_from_db()
        location = self.lokale_overheid.locaties.get()
        self.assertEqual(location.naam, "Name")
        self.assertEqual(location.straat, "Street")
        self.assertEqual(location.nummer, 91)
        self.assertEqual(location.plaats, "Town")
        self.assertEqual(location.postcode, "1234AB")
        self.assertEqual(location.land, "Country")
