from django.db import models
from django.utils.translation import ugettext_lazy as _


class Token(models.Model):
    """Custom authorization token model without binding to a specific user."""

    key = models.CharField(_("key"), max_length=40, primary_key=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        verbose_name = _("token")
        verbose_name_plural = _("tokens")

    def __str__(self):
        return self.key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        """Generate a random key."""
        from django.utils.crypto import get_random_string

        return get_random_string(
            length=40, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456789"
        )
