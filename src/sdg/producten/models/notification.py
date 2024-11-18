from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class NotificationViewed(models.Model):
    gebruiker = models.OneToOneField(User, on_delete=models.CASCADE)
    last_viewed_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User: {self.gebruiker_id} - Notification last viewed on: {self.last_viewed_date}"
