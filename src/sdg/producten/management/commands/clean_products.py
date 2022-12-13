from django.core.management import BaseCommand

from sdg.producten.models import LocalizedProduct

previous_placeholder_texts = {
    "product_aanwezig_toelichting": {
        "en": [
            "The municipality of {lokale_overheid} doesn't offer {product}.",
            "The municipality of {lokale_overheid} doesn't offer {product} because...",
        ],
        "nl": [
            "De gemeente {lokale_overheid} levert het product {product} niet.",
            "De gemeente {lokale_overheid} levert het product {product} niet omdat...",
        ],
    },
    "product_valt_onder_toelichting": {
        "en": [
            "In the municipality of {lokale_overheid}, {product} falls under [product]."
        ],
        "nl": [
            "In de gemeente {lokale_overheid} is {product} onderdeel van [product]."
        ],
    },
}


class Command(BaseCommand):
    help = "Clean all products according to standard rules."

    def handle(self, **options):
        qs = LocalizedProduct.objects.all()
        qs = qs.select_related(
            "product_versie__product__catalogus__lokale_overheid",
            "product_versie__product__catalogus__lokale_overheid__organisatie",
            "product_versie__product__generiek_product",
        )
        localized_products = qs.prefetch_related(
            "product_versie__product__generiek_product__vertalingen"
        )

        for localized_product in localized_products:
            self.clean_localized_product(localized_product)

    @staticmethod
    def format_placeholder_text(text, *, generic_product, municipality, language):
        """
        Format the placeholder text.
        """
        generic_languages = generic_product.vertalingen.all()
        result = [i for i in generic_languages if i.taal == language]
        localized_generic_product = result[0]

        return text.format(
            lokale_overheid=municipality,
            product=localized_generic_product,
        )

    def clean_explanation(
        self,
        localized_product,
        field_name,
    ):
        """
        Clean the explanation of a localized product.

        This is a fix for broken placeholder texts as a result of changes.
        """
        language = localized_product.taal
        generic_product = localized_product.product_versie.product.generiek_product
        municipality = (
            localized_product.product_versie.product.catalogus.lokale_overheid
        )

        for text in previous_placeholder_texts[field_name][language]:
            formatted_text = self.format_placeholder_text(
                text,
                generic_product=generic_product,
                municipality=municipality,
                language=language,
            )
            if getattr(localized_product, field_name) == formatted_text:
                setattr(localized_product, field_name, "")
                self.stdout.write(f"Cleaned {field_name} for {localized_product}")
                return

    def clean_localized_product(self, localized_product):
        """
        Clean a localized product.
        """
        self.clean_explanation(localized_product, "product_aanwezig_toelichting")
        self.clean_explanation(localized_product, "product_valt_onder_toelichting")
        localized_product.save()
