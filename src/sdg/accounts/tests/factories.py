from django.contrib.auth import get_user_model
from django.utils.timezone import now

import factory
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    username = factory.Faker("user_name")
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
