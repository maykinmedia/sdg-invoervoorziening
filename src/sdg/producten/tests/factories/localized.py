import factory.fuzzy
from factory.django import DjangoModelFactory

from sdg.core.constants import TaalChoices
from sdg.producten.models import LocalizedGeneriekProduct, LocalizedProduct
from sdg.producten.tests.factories.product import (
    GeneriekProductFactory,
    ReferentieProductVersieFactory,
    SpecifiekProductVersieFactory,
)


class LocalizedGeneriekProductFactory(DjangoModelFactory):
    uuid = factory.Faker("uuid4")
    generiek_product = factory.SubFactory(GeneriekProductFactory)

    datum_check = factory.Faker("date_this_month", before_today=True)
    laatst_gewijzigd = factory.Faker("date_this_month", before_today=True)

    product_titel = factory.Faker("word")

    generieke_tekst = factory.Faker("paragraph")
    korte_omschrijving = factory.Faker("sentence")
    landelijke_link = factory.Faker("url", schemes=["https"])

    taal = factory.Sequence(lambda n: TaalChoices.get_available_languages()[n % 2])

    class Meta:
        model = LocalizedGeneriekProduct


class LocalizedProductFactory(DjangoModelFactory):
    taal = factory.Sequence(lambda n: TaalChoices.get_available_languages()[n % 2])

    product_titel_decentraal = factory.Faker("word")
    bewijs = factory.Faker("paragraph")
    bezwaar_en_beroep = factory.Faker("paragraph")
    datum_wijziging = factory.Faker("paragraph")

    decentrale_procedure_label = factory.Faker("word")
    decentrale_procedure_link = factory.Faker("url", schemes=["https"])

    kosten_en_betaalmethoden = factory.Faker("paragraph")
    procedure_beschrijving = factory.Faker("paragraph")
    specifieke_tekst = factory.Faker("paragraph")
    uiterste_termijn = factory.Faker("paragraph")
    vereisten = factory.Faker("paragraph")
    wtd_bij_geen_reactie = factory.Faker("paragraph")

    verwijzing_links = [
        ["label1", "https://example.com"],
        ["label2", "https://example2.com"],
    ]

    class Meta:
        model = LocalizedProduct


class LocalizedReferentieProductFactory(LocalizedProductFactory):
    product_versie = factory.SubFactory(ReferentieProductVersieFactory)


class LocalizedSpecifiekProductFactory(LocalizedProductFactory):
    product_versie = factory.SubFactory(SpecifiekProductVersieFactory)
