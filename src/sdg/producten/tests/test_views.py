from django_webtest import WebTest

from sdg.accounts.tests.factories import RoleFactory, SuperUserFactory, UserFactory
from sdg.core.tests.constants import Status
from sdg.producten.tests.factories.localized import (
    LocalizedGeneriekProductFactory,
    LocalizedProductFactory,
)
from sdg.producten.tests.factories.product import (
    ProductVersieFactory,
    ReferentieProductVersieFactory,
    SpecifiekProductFactory,
    SpecifiekProductVersieFactory,
)

PRODUCT_EDIT = "producten:edit"
PRODUCT_DETAIL = "producten:detail"

TAB_NL = ".tabs #nl"
TAB_EN = ".tabs #en"


class ProductDetailViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.app.set_user(self.user)

    def test_unavailable_product_displays_warning(self):
        product = SpecifiekProductFactory.create(beschikbaar=False)
        product_version = ProductVersieFactory.create(product=product)
        LocalizedProductFactory.create_batch(2, product_versie=product_version)
        RoleFactory.create(
            user=self.user, lokale_overheid=product.catalogus.lokale_overheid
        )

        response = self.app.get(product_version.product.get_absolute_url())
        self.assertEqual(response.status_code, Status.OK)

        self.assertIn("Dit product is van de productenlijst verwijderd.", response.text)

    def test_generic_information_is_displayed_next_to_information(self):
        product_version = SpecifiekProductVersieFactory.create()

        generic_nl, generic_en = LocalizedGeneriekProductFactory.create_batch(
            2, generiek_product=product_version.product.generic_product
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_version)

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
        )

        response = self.app.get(product_version.product.get_absolute_url())
        self.assertEqual(response.status_code, Status.OK)

        text_nl = response.pyquery(TAB_NL).text()
        text_en = response.pyquery(TAB_EN).text()

        self.assertIn(generic_nl.product_titel, text_nl)
        self.assertIn(generic_nl.generieke_tekst, text_nl)
        self.assertIn(generic_nl.korte_omschrijving, text_nl)

        self.assertIn(generic_en.product_titel, text_en)
        self.assertIn(generic_en.generieke_tekst, text_en)
        self.assertIn(generic_en.korte_omschrijving, text_en)

    def test_reference_product_details_are_displayed(self):
        product_version = ReferentieProductVersieFactory.create()
        reference_nl, reference_en = LocalizedProductFactory.create_batch(
            2, product_versie=product_version
        )

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
        )

        response = self.app.get(product_version.product.get_absolute_url())
        self.assertEqual(response.status_code, Status.OK)

        text_nl = response.pyquery(TAB_NL).text()
        text_en = response.pyquery(TAB_EN).text()

        self.assertIn(reference_nl.product_titel_decentraal, text_nl)
        self.assertIn(reference_nl.specifieke_tekst, text_nl)
        self.assertIn(reference_nl.specifieke_link, text_nl)

        self.assertIn(reference_en.product_titel_decentraal, text_en)
        self.assertIn(reference_en.specifieke_tekst, text_en)
        self.assertIn(reference_en.specifieke_link, text_en)

    def test_specific_product_details_are_displayed(self):
        product_version = SpecifiekProductVersieFactory.create()
        specific_nl, specific_en = LocalizedProductFactory.create_batch(
            2, product_versie=product_version
        )

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
        )

        response = self.app.get(product_version.product.get_absolute_url())
        self.assertEqual(response.status_code, Status.OK)

        text_nl = response.pyquery(TAB_NL).text()
        text_en = response.pyquery(TAB_EN).text()

        self.assertIn(specific_nl.product_titel_decentraal, text_nl)
        self.assertIn(specific_nl.specifieke_tekst, text_nl)
        self.assertIn(specific_nl.specifieke_link, text_nl)

        self.assertIn(specific_en.product_titel_decentraal, text_en)
        self.assertIn(specific_en.specifieke_tekst, text_en)
        self.assertIn(specific_en.specifieke_link, text_en)

    def test_reference_product_fills_missing_specific_fields(self):
        product_version = SpecifiekProductVersieFactory.create()
        reference_product = product_version.product.referentie_product

        specific_nl, specific_en = LocalizedProductFactory.create_batch(
            2,
            product_versie=product_version,
            specifieke_tekst="",
            specifieke_link="",
        )

        reference_versie = ProductVersieFactory.create(product=reference_product)
        reference_nl, reference_en = LocalizedProductFactory.create_batch(
            2, product_versie=reference_versie
        )

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
        )

        response = self.app.get(product_version.product.get_absolute_url())
        self.assertEqual(response.status_code, Status.OK)

        text_nl = response.pyquery(TAB_NL).text()
        text_en = response.pyquery(TAB_EN).text()

        self.assertIn(specific_nl.product_titel_decentraal, text_nl)
        self.assertIn(reference_nl.specifieke_tekst, text_nl)
        self.assertIn(reference_nl.specifieke_link, text_nl)

        self.assertIn(specific_en.product_titel_decentraal, text_en)
        self.assertIn(reference_en.specifieke_tekst, text_en)
        self.assertIn(reference_en.specifieke_link, text_en)


class ReferentieProductUpdateViewTests(WebTest):
    ...


class SpecifiekProductUpdateViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.superuser = SuperUserFactory.create()
        self.app.set_user(self.superuser)
        self.specific_product = SpecifiekProductFactory.create()

    def test_unavailable_product_displays_warning(self):
        ...

    def test_publish_now(self):
        ...

    def test_publish_now_existing_now(self):
        ...

    def test_publish_now_existing_concept(self):
        ...

    def test_publish_now_existing_later(self):
        ...

    def test_publish_concept(self):
        ...

    def test_publish_later(self):
        ...

    def test_publish_concept_existing_concept(self):
        ...

    def test_publish_later_existing_concept(self):
        ...
