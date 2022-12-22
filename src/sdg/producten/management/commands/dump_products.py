import json

from django.core.management import BaseCommand
from django.http import HttpRequest

from sdg.api.views import ProductViewSet

OUTPUT_FILE = "products.json"


class Command(BaseCommand):
    help = "Dump all products to a JSON file."

    def handle(self, **options):
        class auth:
            api_default_most_recent = True

        request = HttpRequest()
        request.auth = auth
        request.META["SERVER_NAME"] = "localhost"
        request.META["SERVER_PORT"] = 0

        _ViewSet = ProductViewSet()
        _Serializer = _ViewSet.get_serializer_class()
        _ViewSet.request = request

        serializer = _Serializer(
            _ViewSet.get_queryset(), many=True, context={"request": request}
        )

        dump = json.dumps(serializer.data, indent=4)

        with open(OUTPUT_FILE, "w") as f:
            f.write(dump)

        self.stdout.write(dump)
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully dumped {len(serializer.data)} products (filename: {OUTPUT_FILE})"
            )
        )
