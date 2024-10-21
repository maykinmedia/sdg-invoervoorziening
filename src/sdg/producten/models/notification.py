from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class NotificationViewed(models.Model):
    gebruiker = models.OneToOneField(User, on_delete=models.CASCADE)
    last_viewed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.gebruiker} - Notification last viewed on: {self.last_viewed_date}"
        )
