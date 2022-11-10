from datetime import datetime
from unittest import skip

from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext as _

from django_webtest import WebTest
from freezegun import freeze_time

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.core.constants import GenericProductStatus
from sdg.core.models import ProductenCatalogus
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import OverheidsorganisatieFactory
from sdg.organisaties.tests.factories.overheid import (
    BevoegdeOrganisatieFactory,
    LocatieFactory,
    LokaleOverheidFactory,
)
from sdg.producten.tests.factories.localized import (
    LocalizedReferentieProductFactory,
    LocalizedSpecifiekProductFactory,
)
from sdg.producten.tests.factories.product import (
    GeneriekProductFactory,
    ReferentieProductFactory,
    SpecifiekProductFactory,
)

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

    @override_settings(SDG_CMS_PRODUCTS_DISABLED=True)
    def test_unable_to_see_catalog_with_setting_cms_products_disabled(self):
        lokale_overheid = LokaleOverheidFactory.create()
        RoleFactory.create(
            user=self.user,
            lokale_overheid=lokale_overheid,
            is_redacteur=True,
        )
        response = self.app.get(lokale_overheid.get_absolute_url())
        self.assertIn(
            _(
                "Je kan producten niet beheren in het CMS maar enkel via de API. Je kan wel via het menu bovenin de organisatie gegevens, locaties en bevoegde organisaties beheren."
            ),
            response.text,
        )

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
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.test_specific_products_are_displayed.com",
            owms_pref_label="test_specific_products_are_displayed",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
        )
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            naam="test_specific_products_are_displayed",
            organisatie=organisatie,
            lokale_overheid=lokale_overheid,
        )
        reference_catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True
        )
        reference_products = ReferentieProductFactory.create_batch(
            3,
            catalogus=reference_catalog,
            bevoegde_organisatie=bevoegde_organisatie,
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
                product_versie__product__bevoegde_organisatie=bevoegde_organisatie,
            )
            localized_specific_product = LocalizedSpecifiekProductFactory.create(
                product_versie__product__referentie_product=reference_product,
                product_versie__product__catalogus=specific_catalog,
                product_versie__product__bevoegde_organisatie=bevoegde_organisatie,
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

    def test_reference_products_are_displayed_only_if_ready_for_admin(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.test_specific_products_are_displayed.com",
            owms_pref_label="test_specific_products_are_displayed",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
        )
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            naam="test_specific_products_are_displayed",
            organisatie=organisatie,
            lokale_overheid=lokale_overheid,
        )
        reference_catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=True
        )

        generic_ready_for_publication = GeneriekProductFactory.create(
            product_status=GenericProductStatus.READY_FOR_PUBLICATION,
        )
        generic_ready_for_admin = GeneriekProductFactory.create(
            product_status=GenericProductStatus.READY_FOR_ADMIN,
        )
        generic_new = GeneriekProductFactory.create(
            product_status=GenericProductStatus.NEW,
        )
        generic_deleted = GeneriekProductFactory.create(
            product_status=GenericProductStatus.DELETED,
        )

        reference_ready_for_publication = ReferentieProductFactory.create(
            generiek_product=generic_ready_for_publication,
            catalogus=reference_catalog,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        reference_ready_for_admin = ReferentieProductFactory.create(
            generiek_product=generic_ready_for_admin,
            catalogus=reference_catalog,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        reference_new = ReferentieProductFactory.create(
            generiek_product=generic_new,
            catalogus=reference_catalog,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        reference_deleted = ReferentieProductFactory.create(
            generiek_product=generic_deleted,
            catalogus=reference_catalog,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        reference_lokale_overheid = reference_catalog.lokale_overheid

        reference_products = [
            reference_ready_for_publication,
            reference_ready_for_admin,
            reference_new,
            reference_deleted,
        ]

        for reference_product in reference_products:
            LocalizedReferentieProductFactory.create(
                product_versie__product=reference_product,
                product_versie__product__catalogus=reference_catalog,
                product_versie__product__bevoegde_organisatie=bevoegde_organisatie,
            )

        RoleFactory.create(
            user=self.user,
            lokale_overheid=reference_lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(reference_lokale_overheid.get_absolute_url())

        response_text = response.text.lower()

        self.assertEqual(response.pyquery(CATALOG_SELECTOR).length, 1)
        self.assertEqual(response.pyquery(PRODUCT_SELECTOR).length, 1)
        self.assertIn(str(reference_ready_for_admin), response_text)
        self.assertNotIn(str(reference_ready_for_publication), response_text)
        self.assertNotIn(str(reference_new), response_text)
        self.assertNotIn(str(reference_deleted), response_text)

    def test_specific_products_are_displayed_only_if_ready_for_publication(self):
        organisatie = OverheidsorganisatieFactory.create(
            owms_identifier="https://www.test_specific_products_are_displayed.com",
            owms_pref_label="test_specific_products_are_displayed",
            owms_end_date=None,
        )
        lokale_overheid = LokaleOverheidFactory.create(
            automatisch_catalogus_aanmaken=False,
            organisatie=organisatie,
        )
        bevoegde_organisatie = BevoegdeOrganisatieFactory.create(
            naam="test_specific_products_are_displayed",
            organisatie=organisatie,
            lokale_overheid=lokale_overheid,
        )
        specific_catalog = ProductenCatalogusFactory.create(
            is_referentie_catalogus=False
        )

        generic_ready_for_publication = GeneriekProductFactory.create(
            product_status=GenericProductStatus.READY_FOR_PUBLICATION,
        )
        generic_ready_for_admin = GeneriekProductFactory.create(
            product_status=GenericProductStatus.READY_FOR_ADMIN,
        )
        generic_new = GeneriekProductFactory.create(
            product_status=GenericProductStatus.NEW,
        )
        generic_deleted = GeneriekProductFactory.create(
            product_status=GenericProductStatus.DELETED,
        )

        specific_ready_for_publication = SpecifiekProductFactory.create(
            generiek_product=generic_ready_for_publication,
            catalogus=specific_catalog,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        specific_ready_for_admin = SpecifiekProductFactory.create(
            generiek_product=generic_ready_for_admin,
            catalogus=specific_catalog,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        specific_new = SpecifiekProductFactory.create(
            generiek_product=generic_new,
            catalogus=specific_catalog,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        specific_deleted = SpecifiekProductFactory.create(
            generiek_product=generic_deleted,
            catalogus=specific_catalog,
            bevoegde_organisatie=bevoegde_organisatie,
        )
        specific_lokale_overheid = specific_catalog.lokale_overheid

        specific_products = [
            specific_ready_for_publication,
            specific_ready_for_admin,
            specific_new,
            specific_deleted,
        ]

        for specific_product in specific_products:
            LocalizedReferentieProductFactory.create(
                product_versie__product=specific_product,
                product_versie__product__catalogus=specific_catalog,
                product_versie__product__bevoegde_organisatie=bevoegde_organisatie,
            )

        RoleFactory.create(
            user=self.user,
            lokale_overheid=specific_lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(specific_lokale_overheid.get_absolute_url())

        response_text = response.text.lower()

        self.assertEqual(response.pyquery(CATALOG_SELECTOR).length, 1)
        self.assertEqual(response.pyquery(PRODUCT_SELECTOR).length, 1)
        self.assertNotIn(str(specific_ready_for_admin), response_text)
        self.assertIn(str(specific_ready_for_publication), response_text)
        self.assertNotIn(str(specific_new), response_text)
        self.assertNotIn(str(specific_deleted), response_text)

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
            is_beheerder=True,
        )

    def test_can_update_municipality_details(self):
        response = self.app.get(
            reverse(self.url, kwargs={"pk": self.lokale_overheid.pk})
        )

        response.form["contact_website"] = "https://example.com"
        response.form["contact_emailadres"] = "email@example.com"
        response.form["contact_telefoonnummer"] = "0619123123"
        response.form["contact_formulier_link"] = "https://example.com"
        response.form.submit()

        self.lokale_overheid.refresh_from_db()
        self.assertEqual(self.lokale_overheid.contact_website, "https://example.com")
        self.assertEqual(self.lokale_overheid.contact_emailadres, "email@example.com")
        self.assertEqual(self.lokale_overheid.contact_telefoonnummer, "0619123123")
        self.assertEqual(
            self.lokale_overheid.contact_formulier_link, "https://example.com"
        )


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
            is_beheerder=True,
        )

    def test_can_update_municipality_location(self):
        LocatieFactory.create(lokale_overheid=self.lokale_overheid)

        response = self.app.get(
            reverse(self.url, kwargs={"pk": self.lokale_overheid.pk})
        )

        response.form["form-0-naam"] = "Name"
        response.form["form-0-straat"] = "Street"
        response.form["form-0-nummer"] = "91"
        response.form["form-0-plaats"] = "Town"
        response.form["form-0-postcode"] = "1234AB"
        response.form["form-0-land"] = "Country"
        response.form.submit()

        self.lokale_overheid.refresh_from_db()
        location = self.lokale_overheid.locaties.get()
        self.assertEqual(location.naam, "Name")
        self.assertEqual(location.straat, "Street")
        self.assertEqual(location.nummer, "91")
        self.assertEqual(location.plaats, "Town")
        self.assertEqual(location.postcode, "1234AB")
        self.assertEqual(location.land, "Country")
