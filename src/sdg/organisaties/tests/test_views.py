from django_webtest import WebTest

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.core.models import ProductenCatalogus
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.organisaties.tests.factories.overheid import (
    LokaleOverheidFactory,
    LokatieFactory,
)
from sdg.producten.tests.factories.localized import (
    LocalizedReferentieProductFactory,
    LocalizedSpecifiekProductFactory,
)
from sdg.producten.tests.factories.product import ReferentieProductFactory

CATALOG_SELECTOR = ".products__title"
PRODUCT_SELECTOR = ".products__item"


class LokaleOverheidDetailViewTests(WebTest):
    # TODO: Add tests for product icons

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

    def test_municipality_details_are_displayed(self):
        lokale_overheid = LokaleOverheidFactory.create()
        lokaties = LokatieFactory.create_batch(3, lokale_overheid=lokale_overheid)
        RoleFactory.create(
            user=self.user, lokale_overheid=lokale_overheid, is_redacteur=True
        )

        response = self.app.get(lokale_overheid.get_absolute_url())
        response_text = response.text

        self.assertIn(str(lokale_overheid), response_text)
        self.assertIn(lokale_overheid.contact_website, response_text)
        self.assertIn(lokale_overheid.contact_telefoonnummer, response_text)
        self.assertIn(lokale_overheid.contact_emailadres, response_text)
        for lokatie in lokaties:
            self.assertIn(str(lokatie), response_text)
            self.assertIn(lokatie.postcode, response_text)
            self.assertIn(lokatie.maandag[0], response_text)

    def test_specific_catalog_is_automatically_generated(self):
        localized_reference_product = LocalizedReferentieProductFactory.create()
        reference_catalog = localized_reference_product.product_versie.product.catalogus
        reference_lokale_overheid = reference_catalog.lokale_overheid

        self.assertEqual(ProductenCatalogus.objects.count(), 1)

        RoleFactory.create(
            user=self.user, lokale_overheid=reference_lokale_overheid, is_redacteur=True
        )

        response = self.app.get(reference_lokale_overheid.get_absolute_url())
        self.assertEqual(ProductenCatalogus.objects.count(), 2)

        self.assertIn(
            reference_catalog.naam,
            response.text,
        )
        self.assertEqual(response.pyquery(CATALOG_SELECTOR).length, 2)

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

        response_text = response.text

        self.assertIn(
            specific_catalog.naam,
            response_text,
        )
        self.assertEqual(response.pyquery(CATALOG_SELECTOR).length, 1)

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

        response_text = response.text

        self.assertEqual(response.pyquery(CATALOG_SELECTOR).length, 1)
        self.assertEqual(response.pyquery(PRODUCT_SELECTOR).length, 3)
        self.assertIn(
            specific_catalog.naam,
            response_text,
        )
        for product in specific_products:
            self.assertIn(
                str(product),
                response_text,
            )

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

        response_text = response.text

        self.assertEqual(response.pyquery(CATALOG_SELECTOR).length, 2)
        self.assertEqual(response.pyquery(PRODUCT_SELECTOR).length, 6)
        self.assertIn(
            specific_catalog.naam,
            response_text,
        )
        for product in specific_products:
            self.assertIn(
                str(product),
                response_text,
            )
