import random
import string

import factory
from factory.django import DjangoModelFactory

from sdg.core.tests.factories.logius import OverheidsorganisatieFactory
from sdg.organisaties.models import (
    BevoegdeOrganisatie,
    LokaleOverheid,
    Lokatie as Locatie,
)


class LokaleOverheidFactory(DjangoModelFactory):
    organisatie = factory.SubFactory(OverheidsorganisatieFactory)
    contact_website = factory.Faker("url")
    contact_telefoonnummer = factory.Faker("phone_number", locale="nl_NL")
    contact_emailadres = factory.Faker("email")
    contact_formulier_link = factory.Faker("url")

    class Meta:
        model = LokaleOverheid


class LocatieFactory(DjangoModelFactory):
    lokale_overheid = factory.SubFactory(LokaleOverheidFactory)
    naam = factory.Sequence(lambda n: str(n))
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
        model = Locatie


class BevoegdeOrganisatieFactory(DjangoModelFactory):
    naam = factory.Sequence(lambda n: str(n))
    organisatie = factory.SubFactory(OverheidsorganisatieFactory)
    lokale_overheid = factory.SubFactory(
        LokaleOverheidFactory, organisatie=factory.SelfAttribute("organisatie")
    )

    class Meta:
        model = BevoegdeOrganisatie
