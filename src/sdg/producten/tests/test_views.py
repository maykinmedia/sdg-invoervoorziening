from django.urls import reverse

from django_webtest import WebTest
from freezegun import freeze_time

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.core.tests.utils import hard_refresh_from_db
from sdg.organisaties.tests.factories.overheid import LokatieFactory
from sdg.producten.models import LocalizedProduct, Product
from sdg.producten.tests.constants import (
    DUMMY_TITLE,
    FUTURE_DATE,
    NOW_DATE,
    PRODUCT_EDIT_URL,
    TAB_EN,
    TAB_NL,
)
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
from sdg.producten.utils import build_url_kwargs


class TestProductCreateRedirectView(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.app.set_user(self.user)

    def test_specific_product_is_created(self):
        reference_product = ReferentieProductVersieFactory.create().product
        RoleFactory.create(
            user=self.user,
            lokale_overheid=reference_product.catalogus.lokale_overheid,
            is_redacteur=True,
        )
        self.assertEqual(0, reference_product.specifieke_producten.count())

        self.app.get(reference_product.get_create_redirect_url())
        self.assertEqual(1, reference_product.specifieke_producten.count())


class ProductDetailViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.app.set_user(self.user)

    def test_unavailable_reference_product_displays_warning(self):
        product = SpecifiekProductFactory.create(
            product_aanwezig=False, referentie_product__product_aanwezig=False
        )
        product_version = ProductVersieFactory.create(product=product)
        LocalizedProductFactory.create_batch(2, product_versie=product_version)
        RoleFactory.create(
            user=self.user,
            lokale_overheid=product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(product_version.product.get_absolute_url())

        self.assertIn(
            "Er is nog geen product tekst gepubliceerd. Er is een concept tekst aanwezig.",
            response.text,
        )

    def test_concept_product_displays_warning(self):
        product = SpecifiekProductFactory.create(
            product_aanwezig=False,
        )
        product_version = ProductVersieFactory.create(
            product=product,
            publicatie_datum=None,
            versie=1,
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_version)
        RoleFactory.create(
            user=self.user,
            lokale_overheid=product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(product_version.product.get_absolute_url())

        self.assertIn(
            "Er is nog geen product tekst gepubliceerd. Er is een concept tekst aanwezig.",
            response.text,
        )

    @freeze_time(NOW_DATE)
    def test_generic_information_is_displayed_next_to_information(self):
        product_version = SpecifiekProductVersieFactory.create(
            versie=1, publicatie_datum=NOW_DATE
        )

        generic_nl, generic_en = LocalizedGeneriekProductFactory.create_batch(
            2, generiek_product=product_version.product.generic_product
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_version)

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(product_version.product.get_absolute_url())

        text_nl = response.pyquery(TAB_NL).text()
        text_en = response.pyquery(TAB_EN).text()

        self.assertIn(generic_nl.product_titel, text_nl)
        self.assertIn(generic_nl.generieke_tekst, text_nl)
        self.assertIn(generic_nl.korte_omschrijving, text_nl)

        self.assertIn(generic_en.product_titel, text_en)
        self.assertIn(generic_en.generieke_tekst, text_en)
        self.assertIn(generic_en.korte_omschrijving, text_en)

    @freeze_time(NOW_DATE)
    def test_reference_product_details_are_displayed(self):
        product_version = ReferentieProductVersieFactory.create(
            versie=1, publicatie_datum=NOW_DATE
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_version)

        reference_nl, reference_en = LocalizedProduct.objects.filter(
            product_versie=product_version
        )

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(product_version.product.get_absolute_url())

        text_nl = response.pyquery(TAB_NL).text()
        text_en = response.pyquery(TAB_EN).text()

        self.assertIn(reference_nl.product_titel_decentraal, text_nl)
        self.assertIn(reference_nl.specifieke_tekst, text_nl)

        self.assertIn(reference_en.product_titel_decentraal, text_en)
        self.assertIn(reference_en.specifieke_tekst, text_en)

    @freeze_time(NOW_DATE)
    def test_specific_product_details_are_displayed(self):
        product_version = SpecifiekProductVersieFactory.create(
            publicatie_datum=NOW_DATE
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_version)
        specific_nl, specific_en = LocalizedProduct.objects.filter(
            product_versie=product_version
        )

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(product_version.product.get_absolute_url())

        text_nl = response.pyquery(TAB_NL).text()
        text_en = response.pyquery(TAB_EN).text()

        self.assertIn(specific_nl.product_titel_decentraal, text_nl)
        self.assertIn(specific_nl.specifieke_tekst, text_nl)

        self.assertIn(specific_en.product_titel_decentraal, text_en)
        self.assertIn(specific_en.specifieke_tekst, text_en)

    @freeze_time(NOW_DATE)
    def test_product_locations_are_displayed(self):
        product_version = SpecifiekProductVersieFactory.create(
            publicatie_datum=NOW_DATE
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_version)
        product = product_version.product
        lokale_overheid = product.catalogus.lokale_overheid
        lokaties = LokatieFactory.create_batch(3, lokale_overheid=lokale_overheid)

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

        product.lokaties.set(lokaties[:2])
        product.save()

        response = self.app.get(product_version.product.get_absolute_url())

        checkboxes = response.pyquery("input[type=checkbox]")
        actual_loc_ids = set(product.lokaties.values_list("pk", flat=True))
        display_loc_ids = {
            int(checkbox.value) for checkbox in checkboxes if checkbox.value is not None
        }
        self.assertSetEqual(actual_loc_ids, display_loc_ids)

    @freeze_time(NOW_DATE)
    def test_reference_product_fills_missing_specific_fields(self):
        product_version = SpecifiekProductVersieFactory.create(
            publicatie_datum=NOW_DATE
        )
        reference_product = product_version.product.referentie_product

        reference_product_version = ProductVersieFactory.create(
            product=reference_product
        )

        LocalizedProductFactory.create_batch(
            2,
            product_versie=product_version,
            specifieke_tekst="",
        )
        LocalizedProductFactory.create_batch(
            2, product_versie=reference_product_version
        )

        specific_nl, specific_en = LocalizedProduct.objects.filter(
            product_versie=product_version
        )
        reference_nl, reference_en = LocalizedProduct.objects.filter(
            product_versie=reference_product_version
        )

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(product_version.product.get_absolute_url())

        text_nl = response.pyquery(TAB_NL).text().lower()
        text_en = response.pyquery(TAB_EN).text().lower()

        self.assertIn(specific_nl.product_titel_decentraal.lower(), text_nl)
        self.assertIn(reference_nl.specifieke_tekst.lower(), text_nl)

        self.assertIn(specific_en.product_titel_decentraal.lower(), text_en)
        self.assertIn(reference_en.specifieke_tekst.lower(), text_en)

    @freeze_time(NOW_DATE)
    def test_published_and_scheduled_shows_active_data_with_schedule_notification(self):
        product_version = SpecifiekProductVersieFactory.create(
            versie=1, publicatie_datum=NOW_DATE
        )
        product = product_version.product
        SpecifiekProductVersieFactory.create(
            versie=2,
            product=product,
            publicatie_datum=FUTURE_DATE,
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_version)

        specific_nl, specific_en = LocalizedProduct.objects.filter(
            product_versie=product_version
        )

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(product_version.product.get_absolute_url())

        text_nl = response.pyquery(TAB_NL).text()

        self.assertIn(specific_nl.product_titel_decentraal, text_nl)
        self.assertIn(specific_nl.specifieke_tekst, text_nl)
        self.assertIn(
            "U heeft nog niet aangegeven of u dit product aanbiedt.", response.text
        )
        self.assertIn(
            "Er staat een nieuwe product tekst klaar om gepubliceerd te worden op . Hieronder ziet u de huidige product tekst.",
            response.text,
        )

    @freeze_time(NOW_DATE)
    def test_published_and_concept_shows_active_data_with_concept_notification(self):
        product_version = SpecifiekProductVersieFactory.create(
            versie=1, publicatie_datum=NOW_DATE
        )
        product = product_version.product
        SpecifiekProductVersieFactory.create(
            versie=2,
            product=product,
            publicatie_datum=None,
        )
        LocalizedProductFactory.create_batch(2, product_versie=product_version)

        specific_nl, specific_en = LocalizedProduct.objects.filter(
            product_versie=product_version
        )

        RoleFactory.create(
            user=self.user,
            lokale_overheid=product_version.product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(product_version.product.get_absolute_url())

        text_nl = response.pyquery(TAB_NL).text()

        self.assertIn(specific_nl.product_titel_decentraal, text_nl)
        self.assertIn(specific_nl.specifieke_tekst, text_nl)
        self.assertIn(
            "U heeft nog niet aangegeven of u dit product aanbiedt.", response.text
        )
        self.assertIn(
            "Er is nog geen product tekst gepubliceerd. Er is een concept tekst aanwezig.",
            response.text,
        )


class SpecifiekProductUpdateViewTests(WebTest):
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

        LocalizedProductFactory.create_batch(2, product_versie=self.product_version)
        LocalizedProductFactory.create_batch(
            2, product_versie=self.reference_product_version
        )

        RoleFactory.create(
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

    def _submit_product_form(self, form, publish_choice: Product.status):
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
        form["date"] = data["date"]
        return form.submit(name="publish", value=data["publish"])

    @freeze_time(NOW_DATE)
    def test_unavailable_reference_product_displays_warning(self):
        self.product.referentie_product.product_aanwezig = False
        self.product.referentie_product.save()
        response = self.app.get(self.product.get_absolute_url())
        self.assertIn(
            "Er is nog geen product tekst gepubliceerd. Er is een concept tekst aanwezig.",
            response.text,
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

        self._submit_product_form(response.form, Product.status.CONCEPT)
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

        self._submit_product_form(response.form, Product.status.PUBLISHED)

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

        self._submit_product_form(response.form, Product.status.SCHEDULED)

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

        self._submit_product_form(response.form, Product.status.CONCEPT)

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

        self._submit_product_form(response.form, Product.status.PUBLISHED)

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

        self._submit_product_form(response.form, Product.status.SCHEDULED)

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

        self._submit_product_form(response.form, Product.status.CONCEPT)

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
        self.assertIn(
            'Indien u kiest voor "Opslaan als concept" dan wordt de publicatie datum verwijderd',
            response.text,
        )

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

        self._submit_product_form(response.form, Product.status.PUBLISHED)

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

        self._submit_product_form(response.form, Product.status.SCHEDULED)

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

        self._submit_product_form(response.form, Product.status.CONCEPT)

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

        self._submit_product_form(response.form, Product.status.PUBLISHED)

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

        self._submit_product_form(response.form, Product.status.SCHEDULED)

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
        LokatieFactory.create_batch(
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

        response.form.fields["product_aanwezig"] = False
        response.form.fields["lokaties"][0].checked = True
        self._submit_product_form(response.form, Product.status.CONCEPT)
        self.product.refresh_from_db()

        locations = list(self.product.get_municipality_locations())
        self.assertTrue(locations[0].is_product_location)
        self.assertFalse(locations[1].is_product_location)
        self.assertFalse(locations[2].is_product_location)
