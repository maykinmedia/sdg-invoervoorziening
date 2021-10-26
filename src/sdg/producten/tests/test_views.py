from django.urls import reverse

from django_webtest import WebTest
from freezegun import freeze_time

from sdg.accounts.tests.factories import RoleFactory, UserFactory
from sdg.organisaties.tests.factories.overheid import LokatieFactory
from sdg.producten.constants import PublishChoices
from sdg.producten.models import LocalizedProduct
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


class ProductDetailViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory.create()
        self.app.set_user(self.user)

    def test_unavailable_reference_product_displays_warning(self):
        product = SpecifiekProductFactory.create(
            beschikbaar=False, referentie_product__beschikbaar=False
        )
        product_version = ProductVersieFactory.create(product=product)
        LocalizedProductFactory.create_batch(2, product_versie=product_version)
        RoleFactory.create(
            user=self.user,
            lokale_overheid=product.catalogus.lokale_overheid,
            is_redacteur=True,
        )

        response = self.app.get(product_version.product.get_absolute_url())

        self.assertIn("Dit product is van de productenlijst verwijderd.", response.text)

    def test_concept_product_displays_warning(self):
        product = SpecifiekProductFactory.create(
            beschikbaar=False,
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

        self.assertIn("Er is een bestaand concept voor dit product.", response.text)

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
        self.assertIn(reference_nl.specifieke_link, text_nl)

        self.assertIn(reference_en.product_titel_decentraal, text_en)
        self.assertIn(reference_en.specifieke_tekst, text_en)
        self.assertIn(reference_en.specifieke_link, text_en)

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
        self.assertIn(specific_nl.specifieke_link, text_nl)

        self.assertIn(specific_en.product_titel_decentraal, text_en)
        self.assertIn(specific_en.specifieke_tekst, text_en)
        self.assertIn(specific_en.specifieke_link, text_en)

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
        self.assertEquals(checkboxes[0].checked, True)
        self.assertEquals(checkboxes[1].checked, True)
        self.assertEquals(checkboxes[2].checked, False)

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
            2, product_versie=product_version, specifieke_tekst="", specifieke_link=""
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

        text_nl = response.pyquery(TAB_NL).text()
        text_en = response.pyquery(TAB_EN).text()

        self.assertIn(specific_nl.product_titel_decentraal, text_nl)
        self.assertIn(reference_nl.specifieke_tekst, text_nl)
        self.assertIn(reference_nl.specifieke_link, text_nl)

        self.assertIn(specific_en.product_titel_decentraal, text_en)
        self.assertIn(reference_en.specifieke_tekst, text_en)
        self.assertIn(reference_en.specifieke_link, text_en)

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
        self.assertIn(specific_nl.specifieke_link, text_nl)
        self.assertIn("Ingeplande wijzigingen op", response.text)

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
        self.assertIn(specific_nl.specifieke_link, text_nl)
        self.assertIn("Er is een bestaand concept voor dit product.", response.text)


class ReferentieProductUpdateViewTests(WebTest):
    ...


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

    def _change_product_status(self, publish_choice: PublishChoices.choices):
        dates = {
            PublishChoices.now: NOW_DATE,
            PublishChoices.concept: None,
            PublishChoices.later: FUTURE_DATE,
        }
        self.product.laatste_versie.publicatie_datum = dates.get(publish_choice)
        self.product.laatste_versie.save()
        self.product.refresh_from_db()
        del self.product.laatste_versie  # clear cached_property

    def _fill_product_form(self, form, publish_choice: PublishChoices.choices):
        form_data = {
            PublishChoices.now: {
                "publish": "now",
            },
            PublishChoices.concept: {
                "publish": "concept",
            },
            PublishChoices.later: {
                "publish": "later",
                "date": FUTURE_DATE,
            },
        }
        data = form_data[publish_choice]
        form["vertalingen-0-product_titel_decentraal"] = data.get("title", DUMMY_TITLE)
        form["date"] = data.get("date", None)
        form["publish"].value = data["publish"]

    @freeze_time(NOW_DATE)
    def test_unavailable_reference_product_displays_warning(self):
        self.product.referentie_product.beschikbaar = False
        self.product.referentie_product.save()
        response = self.app.get(self.product.get_absolute_url())
        self.assertIn("Dit product is van de productenlijst verwijderd.", response.text)

    @freeze_time(NOW_DATE)
    def test_concept_save_concept(self):
        self._change_product_status(PublishChoices.concept)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.concept)
        response.form.submit()
        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 1)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version, None)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.concept)
        self.assertEqual(latest_version.versie, 1)

    @freeze_time(NOW_DATE)
    def test_concept_save_now(self):
        self._change_product_status(PublishChoices.concept)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.now)

        response.form.submit()
        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 1)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(
            latest_active_version.get_published_status(), PublishChoices.now
        )
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.now)
        self.assertEqual(latest_version.versie, 1)

    @freeze_time(NOW_DATE)
    def test_concept_save_later(self):
        self._change_product_status(PublishChoices.concept)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.later)

        response.form.submit()
        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 1)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version, None)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, FUTURE_DATE)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.later)
        self.assertEqual(latest_version.versie, 1)

    @freeze_time(NOW_DATE)
    def test_published_save_concept(self):
        self._change_product_status(PublishChoices.now)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.concept)

        response.form.submit()
        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(
            latest_active_version.get_published_status(), PublishChoices.now
        )
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, None)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.concept)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_save_now(self):
        self._change_product_status(PublishChoices.now)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.now)

        response.form.submit()
        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(
            latest_active_version.get_published_status(), PublishChoices.now
        )
        self.assertEqual(latest_active_version.versie, 2)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.now)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_save_later(self):
        self._change_product_status(PublishChoices.now)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.later)

        response.form.submit()
        self.product_version.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(
            latest_active_version.get_published_status(), PublishChoices.now
        )
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, FUTURE_DATE)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.later)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_scheduled_save_concept(self):
        self._change_product_status(PublishChoices.now)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=FUTURE_DATE,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.concept)

        response.form.submit()
        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(
            latest_active_version.get_published_status(), PublishChoices.now
        )
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, None)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.concept)
        self.assertEqual(latest_version.versie, 2)
        self.assertIn(
            'Indien u kiest voor "Opslaan als concept" dan wordt de publicatie datum verwijderd',
            response.text,
        )

    @freeze_time(NOW_DATE)
    def test_published_and_scheduled_save_now(self):
        self._change_product_status(PublishChoices.now)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=FUTURE_DATE,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.now)

        response.form.submit()
        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(
            latest_active_version.get_published_status(), PublishChoices.now
        )
        self.assertEqual(latest_active_version.versie, 2)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.now)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_scheduled_save_later(self):
        self._change_product_status(PublishChoices.now)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=FUTURE_DATE,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.later)

        response.form.submit()
        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(
            latest_active_version.get_published_status(), PublishChoices.now
        )
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, FUTURE_DATE)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.later)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_concept_save_concept(self):
        self._change_product_status(PublishChoices.now)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=None,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.concept)

        response.form.submit()
        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(
            latest_active_version.get_published_status(), PublishChoices.now
        )
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, None)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.concept)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_concept_save_now(self):
        self._change_product_status(PublishChoices.now)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=None,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.now)

        response.form.submit()
        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(
            latest_active_version.get_published_status(), PublishChoices.now
        )
        self.assertEqual(latest_active_version.versie, 2)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, NOW_DATE)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.now)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_published_and_concept_save_later(self):
        self._change_product_status(PublishChoices.now)
        future_product_version = ProductVersieFactory.create(
            product=self.product,
            publicatie_datum=None,
            versie=2,
        )
        LocalizedProductFactory.create_batch(2, product_versie=future_product_version)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.later)

        response.form.submit()
        self.product.refresh_from_db()

        self.assertEqual(self.product.versies.count(), 2)

        latest_active_version = self.product.laatste_actieve_versie
        latest_version = self.product.laatste_versie
        latest_nl = latest_version.vertalingen.get(taal="nl")

        self.assertEqual(latest_active_version.publicatie_datum, NOW_DATE)
        self.assertEqual(
            latest_active_version.get_published_status(), PublishChoices.now
        )
        self.assertEqual(latest_active_version.versie, 1)

        self.assertEqual(latest_nl.product_titel_decentraal, DUMMY_TITLE)
        self.assertEqual(latest_version.publicatie_datum, FUTURE_DATE)
        self.assertEqual(latest_version.get_published_status(), PublishChoices.later)
        self.assertEqual(latest_version.versie, 2)

    @freeze_time(NOW_DATE)
    def test_can_update_product_information(self):
        self._change_product_status(PublishChoices.concept)
        LokatieFactory.create_batch(
            3, lokale_overheid=self.product.catalogus.lokale_overheid
        )
        locations = list(self.product.get_municipality_locations())
        self.assertEqual(len(locations), 3)
        for location in locations:
            self.assertFalse(location.is_product_location)

        response = self.app.get(
            reverse(PRODUCT_EDIT_URL, kwargs={"pk": self.product.pk})
        )

        self._fill_product_form(response.form, PublishChoices.concept)
        response.form.fields["beschikbaar"] = False
        response.form.fields["lokaties"][0].checked = True
        response.form.submit()
        self.product.refresh_from_db()

        locations = list(self.product.get_municipality_locations())
        self.assertTrue(locations[0].is_product_location)
        self.assertFalse(locations[1].is_product_location)
        self.assertFalse(locations[2].is_product_location)
