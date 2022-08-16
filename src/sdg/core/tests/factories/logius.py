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
    owms_pref_label = factory.Sequence(lambda n: str(n))
    owms_end_date = datetime(day=1, month=1, year=3000)

    class Meta:
        model = Overheidsorganisatie


class InformatiegebiedFactory(DjangoModelFactory):
    informatiegebied = factory.Faker("word")
    informatiegebied_uri = factory.Sequence(
        lambda n: f"http://informatiegebied-uri{n}.org"
    )

    class Meta:
        model = Informatiegebied


class ThemaFactory(DjangoModelFactory):
    code = factory.Sequence(lambda n: n)
    informatiegebied = factory.SubFactory(InformatiegebiedFactory)
    thema = factory.Faker("word")
    thema_uri = factory.Sequence(lambda n: f"http://thema-uri{n}.org")

    class Meta:
        model = Thema


class UniformeProductnaamFactory(DjangoModelFactory):
    thema = factory.SubFactory(ThemaFactory)
    upn_uri = factory.Sequence(lambda n: f"http://upn-uri{n}.com")
    upn_label = factory.Sequence(lambda n: f"upn label {n}")

    class Meta:
        model = UniformeProductnaam
