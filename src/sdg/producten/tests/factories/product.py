import factory
from factory.django import DjangoModelFactory

from sdg.accounts.tests.factories import UserFactory
from sdg.core.tests.factories.catalogus import ProductenCatalogusFactory
from sdg.core.tests.factories.logius import (
    OverheidsorganisatieFactory,
    UniformeProductnaamFactory,
)
from sdg.organisaties.tests.factories.overheid import LokatieFactory
from sdg.producten.models import GeneriekProduct, Product, ProductVersie


class GeneriekProductFactory(DjangoModelFactory):
    upn = factory.SubFactory(UniformeProductnaamFactory)
    verantwoordelijke_organisatie = factory.SubFactory(OverheidsorganisatieFactory)
    verplicht_product = factory.Faker("pybool")

    class Meta:
        model = GeneriekProduct


class ProductFactory(DjangoModelFactory):
    beschikbaar = True
    lokaties = factory.RelatedFactoryList(LokatieFactory, size=3)

    class Meta:
        model = Product


class ReferentieProductFactory(ProductFactory):
    catalogus = factory.SubFactory(
        ProductenCatalogusFactory, is_referentie_catalogus=True
    )
    generiek_product = factory.SubFactory(GeneriekProductFactory)
    referentie_product = None


class SpecifiekProductFactory(ProductFactory):
    catalogus = factory.SubFactory(
        ProductenCatalogusFactory, is_referentie_catalogus=False
    )
    referentie_product = factory.SubFactory(ReferentieProductFactory)
    generiek_product = None


class ProductVersieFactory(DjangoModelFactory):
    gemaakt_door = factory.SubFactory(UserFactory)
    versie = factory.Sequence(lambda n: n + 1)
    publicatie_datum = None

    class Meta:
        model = ProductVersie


class ReferentieProductVersieFactory(ProductVersieFactory):
    product = factory.SubFactory(ReferentieProductFactory)


class SpecifiekProductVersieFactory(ProductVersieFactory):
    product = factory.SubFactory(SpecifiekProductFactory)
