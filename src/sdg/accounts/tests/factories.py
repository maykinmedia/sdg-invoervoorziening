from django.contrib.auth import get_user_model
from django.utils.timezone import now

import factory
from factory.django import DjangoModelFactory

from sdg.accounts.models import Role
from sdg.organisaties.tests.factories.overheid import LokaleOverheidFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence(
        lambda n: "test{1}{0}@maykinmedia.nl".format(now().timestamp(), n)
    )
    password = factory.PostGenerationMethodCall("set_password", "password")

    class Meta:
        model = User


class SuperUserFactory(UserFactory):
    is_staff = True
    is_superuser = True


class RoleFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    lokale_overheid = factory.SubFactory(LokaleOverheidFactory)
    is_beheerder = False
    is_redacteur = False
    is_raadpleger = False
    ontvangt_mail = False

    class Meta:
        model = Role
