from factory.django import DjangoModelFactory

from ...models import ApplicationRapport


class ApplicationExportFactory(DjangoModelFactory):
    class Meta:
        model = ApplicationRapport
