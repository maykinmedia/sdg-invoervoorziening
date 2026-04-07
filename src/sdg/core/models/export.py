from django.db import models
from django.utils.translation import gettext_lazy as _

from privates.fields import PrivateMediaFileField


class ApplicationRapport(models.Model):
    file = PrivateMediaFileField(upload_to="application/rapports", null=True)
    gemaakt_op = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("applicatie rapports")
        verbose_name_plural = _("applicatie rapports")
        ordering = ("-gemaakt_op",)
