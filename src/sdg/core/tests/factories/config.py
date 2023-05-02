import datetime

import factory
from factory.django import DjangoModelFactory

from sdg.core.models.config import SiteConfiguration


class SiteConfigurationFactory(DjangoModelFactory):
    documentatie_titel = factory.Faker("word")
    documentatie_link = factory.Faker("url")
    goatcounter_domain = factory.Faker("word")
    mail_text_changes_last_sent = datetime.date.today()

    class Meta:
        model = SiteConfiguration
