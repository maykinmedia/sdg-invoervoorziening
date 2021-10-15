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
    contact_naam = factory.Faker("name")
    contact_website = factory.Faker("url")
    contact_telefoonnummer = factory.Faker("phone_number", locale="nl_NL")
    contact_emailadres = factory.Faker("email")

    class Meta:
        model = LokaleOverheid


class LokatieFactory(DjangoModelFactory):
    lokale_overheid = factory.SubFactory(LokaleOverheidFactory)
    naam = factory.Faker("color_name")
    straat = factory.Faker("street_name")
    nummer = factory.Faker("building_number")
    postcode = factory.LazyFunction(
        lambda: str(random.randint(1000, 9999))
        + "".join(random.sample(string.ascii_uppercase, k=2)),
    )
    plaats = factory.Faker("city")
    land = factory.Faker("country")
    maandag = ["09:00 - 17:00"]
    dinsdag = ["09:00 - 17:00"]
    woensdag = ["09:00 - 17:00"]
    donderdag = ["09:00 - 17:00"]
    vrijdag = ["09:00 - 17:00"]

    class Meta:
        model = Lokatie
