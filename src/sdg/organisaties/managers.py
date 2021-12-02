from django.db import models


class LokaleOverheidManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "organisatie",
            )
        )
