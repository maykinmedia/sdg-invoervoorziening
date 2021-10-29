from django.db import models


class LocalizedManager(models.Manager):
    def create_localized(self, instance, languages):
        return self.bulk_create(
            [
                instance.generate_localized_information(language=language)
                for language in languages
            ],
            ignore_conflicts=True,
        )
