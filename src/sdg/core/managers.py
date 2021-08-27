from django.db import models
from django.db.models import Q
from django.utils.timezone import now


class OrganisatieManager(models.Manager):
    def active(self):
        return self.filter(Q(owms_end_date__lte=now()))
