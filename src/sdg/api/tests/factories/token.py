import factory
from factory.django import DjangoModelFactory
from sdg.api.models import Token, TokenAuthorization

from sdg.core.tests.factories.logius import OverheidsorganisatieFactory
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory


class TokenFactory(DjangoModelFactory):
    key = factory.Faker("uuid4")
    contact_person = factory.Faker("name")
    email = factory.Faker("email")
    organization = factory.Faker("name")
    application = factory.Faker("word")
    administration = factory.Faker("word")

    class Meta:
        model = Token


class TokenAuthorizationFactory(DjangoModelFactory):
    token = factory.SubFactory(TokenFactory)
    lokale_overheid = factory.SubFactory(LokaleOverheidFactory)

    class Meta:
        model = TokenAuthorization
