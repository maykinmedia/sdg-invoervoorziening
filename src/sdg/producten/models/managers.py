from django.db import models


class LocalizedManager(models.Manager):
    def localize(self, instance, languages):
        """Localize product instance with the given languages."""
        return self.bulk_create(
            [
                instance.generate_localized_information(language=language)
                for language in languages
            ],
            ignore_conflicts=True,
        )

    def bulk_localize(self, instances, languages):
        """Bulk-localize product instances with the given languages."""
        create_list = []
        for instance in instances:  # avoid double list comprehension for readability
            create_list.extend(
                [
                    instance.generate_localized_information(language=language)
                    for language in languages
                ],
            )
        return self.bulk_create(create_list, ignore_conflicts=True)
