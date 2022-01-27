from django.apps import AppConfig

from sdg.core.events import add_event
from sdg.organisaties.utils import InviteUser


class OrganisatiesConfig(AppConfig):
    name = "sdg.organisaties"

    def ready(self):
        add_event("save_user", InviteUser())
