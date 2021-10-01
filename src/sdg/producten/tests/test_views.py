from django_webtest import WebTest


class ProductDetailViewTests(WebTest):
    ...


class ProductUpdateViewTests(WebTest):
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
