import random
import string

import factory
from factory.django import DjangoModelFactory

from sdg.core.tests.factories.logius import OverheidsorganisatieFactory
from sdg.organisaties.models import LokaleOverheid, Lokatie


class LokaleOverheidFactory(DjangoModelFactory):
    ondersteunings_organisatie = factory.SubFactory(OverheidsorganisatieFactory)
    verantwoordelijke_organisatie = factory.SubFactory(OverheidsorganisatieFactory)
    bevoegde_organisatie = factory.SubFactory(OverheidsorganisatieFactory)
    organisatie = factory.SubFactory(OverheidsorganisatieFactory)

    class Meta:
        model = LokaleOverheid


class LokatieFactory(DjangoModelFactory):
    lokale_overheid = factory.SubFactory(LokaleOverheidFactory)
    naam = factory.Faker("color_name")
    straat = factory.Faker("street_name")
    nummer = factory.Faker("building_number")
    postcode = factory.LazyFunction(
        lambda: str(random.randint(1000, 9999)) + "".join(string.ascii_uppercase),
    )
    plaats = factory.LazyFunction("city")
    land = factory.Faker("country")
    maandag = factory.LazyFunction(lambda: "08:00 - 17:00")
    dinsdag = factory.LazyFunction(lambda: "08:00 - 17:00")
    woensdag = factory.LazyFunction(lambda: "08:00 - 17:00")
    donderdag = factory.LazyFunction(lambda: "08:00 - 17:00")
    vrijdag = factory.LazyFunction(lambda: "08:00 - 17:00")

    class Meta:
        model = Lokatie
