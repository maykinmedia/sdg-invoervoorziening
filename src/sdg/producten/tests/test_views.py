from django.urls import reverse

from django_webtest import WebTest
from freezegun import freeze_time

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.core.tests.utils import hard_refresh_from_db
from sdg.organisaties.tests.factories.overheid import LocatieFactory
from sdg.producten.models import Product
from sdg.producten.tests.constants import (
    DUMMY_TITLE,
    FUTURE_DATE,
    NOW_DATE,
    PRODUCT_EDIT_URL,
)
from sdg.producten.tests.factories.localized import (
    LocalizedGeneriekProductFactory,
    LocalizedProductFactory,
)
from sdg.producten.tests.factories.product import (
    ProductVersieFactory,
    ReferentieProductVersieFactory,
    SpecifiekProductVersieFactory,
)
from sdg.producten.utils import build_url_kwargs


class ProductUpdateViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.app.set_user(self.user)

        self.product_version = SpecifiekProductVersieFactory.create(versie=1)
        self.product = self.product_version.product

        self.reference_product = self.product_version.product.referentie_product
        self.reference_product_version = ProductVersieFactory.create(
            product=self.reference_product, versie=1
        )

        self.test = ReferentieProductVersieFactory.create(
            versie=1, publicatie_datum=NOW_DATE
        )

        LocalizedProductFactory.create_batch(2, product_versie=self.product_version)
        LocalizedGeneriekProductFactory.create_batch(
            2,
            generiek_product=self.product_version.product.referentie_product.generiek_product,
        )
        LocalizedProductFactory.create_batch(2, product_versie=self.test)
        LocalizedProductFactory.create_batch(
            2, product_versie=self.reference_product_version
        )

        self.role = RoleFactory.create(
            user=self.user,
            lokale_overheid=self.product_version.product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

    def _change_product_status(self, publish_choice: Product.status):
        dates = {
            Product.status.PUBLISHED: NOW_DATE,
            Product.status.CONCEPT: None,
            Product.status.SCHEDULED: FUTURE_DATE,
        }
        most_recent_version = self.product.most_recent_version
        most_recent_version.publicatie_datum = dates.get(publish_choice)
        most_recent_version.save()
        most_recent_version.refresh_from_db()
        self.product = hard_refresh_from_db(self.product)

    def _submit_product_form(self, form, publish_choice: Product.status, **kwargs):
        form_data = {
            Product.status.PUBLISHED: {
                "publish": "date",
                "date": NOW_DATE,
            },
            Product.status.CONCEPT: {
                "publish": "concept",
                "date": None,
            },
            Product.status.SCHEDULED: {
                "publish": "date",
                "date": FUTURE_DATE,
            },
        }
        data = form_data[publish_choice]
        form["vertalingen-0-product_titel_decentraal"] = DUMMY_TITLE
        for date_field in form.fields["date"]:
            date_field.value = data["date"]
        form.submit(name="publish", value="date", **kwargs)

    @freeze_time(NOW_DATE)
    def test_concept_save_concept(self):
        self._change_product_status(Product.status.CONCEPT)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.CONCEPT)
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 1)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version, None)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.current_status, Product.status.CONCEPT)
        self.assertEqual(latest_version.versie, 1)

    @freeze_time(NOW_DATE)
    def test_concept_save_now(self):
        self._change_product_status(Product.status.CONCEPT)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.PUBLISHED)
        self.assertEqual(response.status_code, 302)

        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 1)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_version.versie, 1)

    @freeze_time(NOW_DATE)
    def test_concept_save_later(self):
        self._change_product_status(Product.status.CONCEPT)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.SCHEDULED)
        self.assertEqual(response.status_code, 302)

        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 1)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version, None)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, FUTURE_DATE)
        self.assertEqual(latest_version.current_status, Product.status.SCHEDULED)
        self.assertEqual(latest_version.versie, 1)

    @freeze_time(NOW_DATE)
    def test_published_save_concept(self):
        self._change_product_status(Product.status.PUBLISHED)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.CONCEPT)
        self.assertEqual(response.status_code, 302)

        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, None)
        self.assertEqual(latest_version.current_status, Product.status.CONCEPT)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_save_now(self):
        self._change_product_status(Product.status.PUBLISHED)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.PUBLISHED)
        self.assertEqual(response.status_code, 302)

        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 2)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_save_later(self):
        self._change_product_status(Product.status.PUBLISHED)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.SCHEDULED)
        self.assertEqual(response.status_code, 302)

        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, FUTURE_DATE)
        self.assertEqual(latest_version.current_status, Product.status.SCHEDULED)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_scheduled_save_concept(self):
        self._change_product_status(Product.status.PUBLISHED)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=FUTURE_DATE,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        self.assertIn(
            'Als u kiest voor "Opslaan en publiceren", vervalt de reeds ingeplande publicatie. Indien u kiest voor "Opslaan als concept" dan wordt de publicatiedatum verwijderd van de ingeplande publicatie.',
            response.text,
        )

        response = self._submit_product_form(response.form, Product.status.CONCEPT)
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, None)
        self.assertEqual(latest_version.current_status, Product.status.CONCEPT)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_scheduled_save_now(self):
        self._change_product_status(Product.status.PUBLISHED)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=FUTURE_DATE,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.PUBLISHED)
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 2)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_scheduled_save_later(self):
        self._change_product_status(Product.status.PUBLISHED)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=FUTURE_DATE,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.SCHEDULED)
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, FUTURE_DATE)
        self.assertEqual(latest_version.current_status, Product.status.SCHEDULED)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_concept_save_concept(self):
        self._change_product_status(Product.status.PUBLISHED)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=None,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.CONCEPT)
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, None)
        self.assertEqual(latest_version.current_status, Product.status.CONCEPT)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_concept_save_now(self):
        self._change_product_status(Product.status.PUBLISHED)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=None,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.PUBLISHED)
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 2)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_concept_save_later(self):
        self._change_product_status(Product.status.PUBLISHED)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=None,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.SCHEDULED)
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version
        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, FUTURE_DATE)
        self.assertEqual(latest_version.current_status, Product.status.SCHEDULED)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_can_update_product_information(self):
        self._change_product_status(Product.status.CONCEPT)
        LocatieFactory.create_batch(
            3, lokale_overheid=self.product.catalogus.lokale_overheid
        )

        locations = list(self.product.get_municipality_locations())
        self.assertEqual(len(locations), 3)
        for location in locations:
            self.assertFalse(location.is_product_location)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            ),
        )
        self.assertEqual(response.status_code, 200)

        response.form.fields["product_aanwezig"] = False
        response.form.fields["locaties"][0].checked = True

        response = self._submit_product_form(response.form, Product.status.CONCEPT)
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()

        locations = list(self.product.get_municipality_locations())
        self.assertTrue(locations[0].is_product_location)
        self.assertFalse(locations[1].is_product_location)
        self.assertFalse(locations[2].is_product_location)

    @freeze_time(NOW_DATE)
    def test_update_product_edited_fields(self):
        self._change_product_status(Product.status.PUBLISHED)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response = self._submit_product_form(response.form, Product.status.PUBLISHED)
        self.assertEqual(response.status_code, 302)

        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 2)
        self.assertEqual(
            latest_active_version.bewerkte_velden,
            [
                {
                    "field": "product_titel_decentraal",
                    "label": "Product titel decentraal",
                    "language": "nl",
                    "flag": "nl",
                },
                {
                    "field": "verwijzing_links",
                    "label": "Verwijzing links",
                    "language": "nl",
                    "flag": "nl",
                },
                {
                    "field": "verwijzing_links",
                    "label": "Verwijzing links",
                    "language": "en",
                    "flag": "gb",
                },
            ],
        )

    @freeze_time(NOW_DATE)
    def test_update_product_internal_remarks(self):
        self._change_product_status(Product.status.PUBLISHED)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        response.form["interne_opmerkingen"] = "test internal remarks"
        response = self._submit_product_form(response.form, Product.status.PUBLISHED)
        self.assertEqual(response.status_code, 302)

        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.active_version

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 2)
        self.assertEqual(
            latest_active_version.interne_opmerkingen, "test internal remarks"
        )

    @freeze_time(NOW_DATE)
    def test_history_displays_reference_version(self):
        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        revisions = response.pyquery(".revision-list")
        self.assertEqual(len(revisions), 2)
        self.assertIn(str(self.product), revisions[0].text_content())
        self.assertIn(str(self.reference_product), revisions[1].text_content())

    @freeze_time(NOW_DATE)
    def test_consultant__cannot_update_product(self):
        self.role.is_redacteur = False
        self.role.is_raadpleger = True
        self.role.save()
        self._change_product_status(Product.status.CONCEPT)
        LocatieFactory.create_batch(
            3, lokale_overheid=self.product.catalogus.lokale_overheid
        )

        locations = list(self.product.get_municipality_locations())
        self.assertEqual(len(locations), 3)
        for location in locations:
            self.assertFalse(location.is_product_location)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            ),
        )
        self.assertEqual(response.status_code, 200)

        response.form.fields["product_aanwezig"] = False
        response.form.fields["locaties"][0].checked = True

        self._submit_product_form(
            response.form,
            Product.status.CONCEPT,
            status=403,
        )
