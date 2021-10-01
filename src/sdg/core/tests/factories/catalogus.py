import string

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from sdg.core.models import ProductenCatalogus
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory


class ProductenCatalogusFactory(DjangoModelFactory):
    lokale_overheid = factory.SubFactory(LokaleOverheidFactory)
    domein = fuzzy.FuzzyText(length=5, chars=string.ascii_uppercase)
    versie = factory.Sequence(lambda n: n)
    naam = factory.Sequence(lambda n: f"catalogus {n}")
    toelichting = factory.Sequence(lambda n: f"toelichting {n}")

    class Meta:
        model = ProductenCatalogus
