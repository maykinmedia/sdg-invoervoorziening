from django.db import models
from django.db.models import Q
from django.utils.timezone import now


class LokaleOverheidQuerySet(models.QuerySet):
    def active_organization(self):
        """
        Filter the municipalities to only include municipalities from active organizations.
        """
        return self.filter(
            Q(organisatie__owms_end_date__gte=now())
            | Q(organisatie__owms_end_date__isnull=True)
        )


class LokaleOverheidManager(models.Manager.from_queryset(LokaleOverheidQuerySet)):
    def get_queryset(self):
        return super().get_queryset().select_related("organisatie")
