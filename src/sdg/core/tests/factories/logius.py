from datetime import datetime

import factory
from factory.django import DjangoModelFactory

from sdg.core.models import (
    Informatiegebied,
    Overheidsorganisatie,
    Thema,
    UniformeProductnaam,
)


class OverheidsorganisatieFactory(DjangoModelFactory):
    owms_identifier = factory.Sequence(lambda n: f"OWMS #{n}")
    owms_pref_label = factory.Faker("word")
    owms_end_date = datetime(day=1, month=1, year=3000)

    class Meta:
        model = Overheidsorganisatie


class InformatiegebiedFactory(DjangoModelFactory):
    code = factory.Sequence(lambda n: n)
    informatiegebied = factory.Faker("word")
    informatiegebied_uri = factory.Faker("url")

    class Meta:
        model = Informatiegebied


class ThemaFactory(DjangoModelFactory):
    informatiegebied = factory.SubFactory(InformatiegebiedFactory)
    thema = factory.Faker("word")
    thema_uri = factory.Faker("url")

    class Meta:
        model = Thema


class UniformeProductnaamFactory(DjangoModelFactory):
    thema = factory.SubFactory(ThemaFactory)
    upn_uri = factory.Faker("url")
    upn_label = factory.Sequence(lambda n: f"upn label {n}")

    rijk = factory.Faker("pybool")
    provincie = factory.Faker("pybool")
    waterschap = factory.Faker("pybool")
    gemeente = factory.Faker("pybool")
    burger = factory.Faker("pybool")
    bedrijf = factory.Faker("pybool")
    dienstenwet = factory.Faker("pybool")
    sdg = factory.Faker("pybool")
    autonomie = factory.Faker("pybool")
    medebewind = factory.Faker("pybool")
    aanvraag = factory.Faker("pybool")
    subsidie = factory.Faker("pybool")
    melding = factory.Faker("pybool")
    verplichting = factory.Faker("pybool")
    digi_d_macht = factory.Faker("pybool")

    grondslag = factory.Faker("word")
    grondslaglabel = factory.Faker("word")
    grondslaglink = factory.Faker("word")

    class Meta:
        model = UniformeProductnaam
