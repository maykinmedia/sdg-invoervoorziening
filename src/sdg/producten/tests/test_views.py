from django.urls import reverse_lazy

from django_webtest import WebTest

from sdg.accounts.tests.factories import SuperUserFactory
from sdg.producten.tests.factories.product import SpecifiekProductFactory

PRODUCT_EDIT = "producten:edit"
PRODUCT_DETAIL = "producten:detail"


class ProductDetailViewTests(WebTest):
    ...


class ReferentieProductUpdateViewTests(WebTest):
    ...


class SpecifiekProductUpdateViewTests(WebTest):
    def setUp(self):
        super().setUp()

        self.superuser = SuperUserFactory.create()
        self.app.set_user(self.superuser)
        self.specific_product = SpecifiekProductFactory.create()

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
