import html
from typing import Optional

from django.test import override_settings
from django.urls import reverse
from django.utils.translation import gettext as _

from django_webtest import WebTest
from freezegun import freeze_time

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.conf.utils import org_type_cfg
from sdg.core.constants import GenericProductStatus, TaalChoices
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

        org_type_cfg.cache_clear()

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

    def _submit_product_form(
        self, form, publish_choice: Optional[Product.status], **kwargs
    ):
        _form_data = {
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
        _submit_value = "date"

        if status_data := _form_data.get(publish_choice):
            for date_field in form.fields["date"]:
                date_field.value = status_data["date"]
            _submit_value = status_data["publish"]

        form["vertalingen-0-product_titel_decentraal"] = DUMMY_TITLE

        return form.submit(
            name="publish",
            value=_submit_value,
            **kwargs,
        )

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
    def test_error_notification_is_displayed(self):
        self._change_product_status(Product.status.CONCEPT)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs=build_url_kwargs(self.product))
        )
        self.assertEqual(response.status_code, 200)

        response.form["vertalingen-0-specifieke_tekst"] = "<a></a>"
        response.form["vertalingen-0-decentrale_procedure_link"] = "bad"
        response = self._submit_product_form(response.form, Product.status.PUBLISHED)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            _(
                "Wijzigingen konden niet worden opgeslagen. Corrigeer de hieronder gemarkeerde fouten."
            ),
            response.text,
        )

    @freeze_time(NOW_DATE)
    def test_success_notification_is_displayed(self):
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

        response = response.follow()
        self.assertIn(
            _("Product {product} is opgeslagen.").format(product=self.product),
            response.text,
        )

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
    def test_product_with_placeholder_warning_displayed(self):
        self._change_product_status(Product.status.CONCEPT)
        self.product.most_recent_version.vertalingen.all().update(
            product_titel_decentraal="[[titel]]"
        )

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            _("De huidige gegevens bevatten placeholder tekst."),
            response.text,
        )

        self.product.most_recent_version.vertalingen.all().update(
            product_titel_decentraal="title XXX"
        )
        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            _("De huidige gegevens bevatten placeholder tekst."),
            response.text,
        )

    @freeze_time(NOW_DATE)
    def test_unable_to_save_product_with_placeholder(self):
        self._change_product_status(Product.status.CONCEPT)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        for date_field in response.form.fields["date"]:
            date_field.value = NOW_DATE

        response.form[
            "vertalingen-0-product_titel_decentraal"
        ] = "Title [[placeholder]]"

        response = response.form.submit(name="publish", value="date")
        self.assertEqual(response.status_code, 200)

        self.assertIn(
            _(
                "Wijzigingen konden niet worden opgeslagen. Corrigeer de hieronder gemarkeerde fouten."
            ),
            response.text,
        )
        self.assertIn(
            _("De tekst mag geen placeholders bevatten."),
            response.text,
        )

        self.product_version.refresh_from_db()
        self.assertEqual(self.product.versies.count(), 1)

    @freeze_time(NOW_DATE)
    def test_able_to_save_product_concept_with_placeholder(self):
        self._change_product_status(Product.status.CONCEPT)

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        for date_field in response.form.fields["date"]:
            date_field.value = None

        response.form[
            "vertalingen-0-product_titel_decentraal"
        ] = "Title [[placeholder]]"

        response = response.form.submit(name="publish", value="concept")
        self.assertEqual(response.status_code, 302)

        self.assertNotIn(
            _(
                "Wijzigingen konden niet worden opgeslagen. Corrigeer de hieronder gemarkeerde fouten."
            ),
            response.text,
        )
        self.assertNotIn(
            _("De tekst mag geen placeholders bevatten."),
            response.text,
        )

        self.product_version.refresh_from_db()
        self.assertEqual(self.product.versies.count(), 1)

        latest_version = self.product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_nl.product_titel_decentraal, "Title [[placeholder]]")
        self.assertEqual(latest_version.publicatie_datum, None)
        self.assertEqual(latest_version.current_status, Product.status.CONCEPT)
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
            None,
            status=403,
        )

    @freeze_time(NOW_DATE)
    @override_settings(SDG_CMS_PRODUCTS_DISABLED=True)
    def test_unable_to_see_product_with_setting_cms_products_disabled(self):
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
        self.assertIn(
            _(
                "Je kan producten niet beheren in het CMS maar enkel via de API. Je kan wel via het menu bovenin de organisatie gegevens, locaties en bevoegde organisaties beheren."
            ),
            response.text,
        )

    @freeze_time(NOW_DATE)
    def test_specific_product_is_editable_if_generic_status_ready_for_publication(self):
        self._change_product_status(Product.status.CONCEPT)
        self.product.generiek_product.product_status = (
            GenericProductStatus.READY_FOR_PUBLICATION
        )
        self.product.generiek_product.save()

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
    def test_specific_product_is_not_found_if_generic_status_is_not_ready_for_publication(
        self,
    ):
        self._change_product_status(Product.status.CONCEPT)

        self.product.generiek_product.product_status = (
            GenericProductStatus.READY_FOR_ADMIN
        )
        self.product.generiek_product.save()
        self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            ),
            status=404,
        )

        self.product.generiek_product.product_status = GenericProductStatus.NEW
        self.product.generiek_product.save()
        self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            ),
            status=404,
        )

        self.product.generiek_product.product_status = GenericProductStatus.DELETED
        self.product.generiek_product.save()
        self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            ),
            status=404,
        )

    @freeze_time(NOW_DATE)
    def test_reference_product_with_placeholder_warning_not_displayed(self):
        self.role = RoleFactory.create(
            user=self.user,
            lokale_overheid=self.reference_product.catalogus.lokale_overheid,
            is_beheerder=True,
        )
        self._change_product_status(Product.status.CONCEPT)
        self.reference_product.generiek_product.product_status = (
            GenericProductStatus.READY_FOR_ADMIN
        )
        self.reference_product.generiek_product.save()
        self.reference_product.most_recent_version.vertalingen.all().update(
            product_titel_decentraal="[[titel]]"
        )

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.reference_product),
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            _("De huidige gegevens bevatten placeholder tekst."),
            response.text,
        )

        self.reference_product.most_recent_version.vertalingen.all().update(
            product_titel_decentraal="title XXX"
        )
        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.reference_product),
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            _("De huidige gegevens bevatten placeholder tekst."),
            response.text,
        )

    @freeze_time(NOW_DATE)
    def test_able_to_save_reference_product_with_placeholder(self):
        self.role = RoleFactory.create(
            user=self.user,
            lokale_overheid=self.reference_product.catalogus.lokale_overheid,
            is_beheerder=True,
        )
        self._change_product_status(Product.status.CONCEPT)
        self.reference_product.generiek_product.product_status = (
            GenericProductStatus.READY_FOR_ADMIN
        )
        self.reference_product.generiek_product.save()
        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.reference_product),
            )
        )
        self.assertEqual(response.status_code, 200)

        for date_field in response.form.fields["date"]:
            date_field.value = NOW_DATE

        response.form[
            "vertalingen-0-product_titel_decentraal"
        ] = "Title [[placeholder]]"

        response = response.form.submit(name="publish", value="date")
        self.assertEqual(response.status_code, 302)

        self.product_version.refresh_from_db()

        self.assertEqual(self.reference_product.versies.count(), 1)

        latest_active_version = self.reference_product.active_version
        latest_version = self.reference_product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, "Title [[placeholder]]")
        self.assertEqual(latest_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_version.versie, 1)

    @freeze_time(NOW_DATE)
    def test_reference_product_is_editable_if_generic_status_ready_for_admin(self):
        self.role = RoleFactory.create(
            user=self.user,
            lokale_overheid=self.reference_product.catalogus.lokale_overheid,
            is_beheerder=True,
        )
        self._change_product_status(Product.status.CONCEPT)
        self.reference_product.generiek_product.product_status = (
            GenericProductStatus.READY_FOR_ADMIN
        )
        self.reference_product.generiek_product.save()

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.reference_product),
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self._submit_product_form(response.form, Product.status.PUBLISHED)
        self.assertEqual(response.status_code, 302)

        self.product_version.refresh_from_db()

        self.assertEqual(self.reference_product.versies.count(), 1)

        latest_active_version = self.reference_product.active_version
        latest_version = self.reference_product.most_recent_version
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_active_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_version.current_status, Product.status.PUBLISHED)
        self.assertEqual(latest_version.versie, 1)

    @freeze_time(NOW_DATE)
    def test_reference_product_is_not_found_if_generic_status_is_not_ready_for_admin_or_pub(
        self,
    ):
        self.role = RoleFactory.create(
            user=self.user,
            lokale_overheid=self.reference_product.catalogus.lokale_overheid,
            is_beheerder=True,
        )
        self._change_product_status(Product.status.CONCEPT)

        self.reference_product.generiek_product.product_status = (
            GenericProductStatus.NEW
        )
        self.reference_product.generiek_product.save()
        self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.reference_product),
            ),
            status=404,
        )

        self.reference_product.generiek_product.product_status = (
            GenericProductStatus.DELETED
        )
        self.reference_product.generiek_product.save()
        self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.reference_product),
            ),
            status=404,
        )

    @freeze_time(NOW_DATE)
    @override_settings(SDG_ORGANIZATION_TYPE="waterauthority")
    def test_version_form_produces_correct_organization_type_data(self):
        self._change_product_status(Product.status.CONCEPT)
        self.product.generiek_product.product_status = (
            GenericProductStatus.READY_FOR_PUBLICATION
        )
        self.product.generiek_product.save()

        response = self.app.get(
            reverse(
                PRODUCT_EDIT_URL,
                kwargs=build_url_kwargs(self.product),
            )
        )
        self.assertEqual(response.status_code, 200)

        municipality = self.product.catalogus.lokale_overheid
        localized_generic_product_en = self.product.generiek_product.vertalingen.get(
            taal="en"
        )
        localized_generic_product_nl = self.product.generiek_product.vertalingen.get(
            taal="nl"
        )

        self.assertIn(
            f"In de waterschap {municipality} is {localized_generic_product_nl} onderdeel van [product].",
            response.text,
        )
        self.assertIn(
            f"In the water authority of {municipality}, {localized_generic_product_en} falls under [product].",
            response.text,
        )
        self.assertIn(
            f"De waterschap {municipality} levert het product {localized_generic_product_nl} niet.",
            response.text,
        )
        self.assertIn(
            f"The water authority of {municipality} doesn't offer {localized_generic_product_en}.",
            html.unescape(response.text),
        )
