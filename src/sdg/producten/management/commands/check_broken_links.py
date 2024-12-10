import time
from collections import defaultdict
from itertools import chain
from urllib import parse

from django.core.management import BaseCommand

import markdown
import requests
from bs4 import BeautifulSoup
from zgw_consumers.concurrent import parallel

from sdg.core.models import ProductFieldConfiguration
from sdg.producten.models import BrokenLinks, LocalizedProduct, Product

FIELD_NAMES_CONFIG = {
    "input_fields": [
        "product_titel_decentraal",
        "product_valt_onder_toelichting",
        "product_aanwezig_toelichting",
    ],
    "markdown_fields": [
        "specifieke_tekst",
        "vereisten",
        "bewijs",
        "procedure_beschrijving",
        "kosten_en_betaalmethoden",
        "uiterste_termijn",
        "bezwaar_en_beroep",
        "wtd_bij_geen_reactie",
    ],
    "urls_fields": [
        "verwijzing_links",
    ],
    "decentrale_label": ["decentrale_procedure_label"],
    "decentrale_link": ["decentrale_procedure_link"],
}
VALID_URL_ADAPTERS = ("tel:", "sms:", "mailto:")
INVALID_URL_ADAPTERS = "geo:"
SUCCES_STATUS_CODE = 200
ANY_ERROR_STATUS_CODE = 420
REDIRECT_STATUS_CODES = {301, 302, 303, 307, 308}
SUCCESSFUL_STATUS_CODES = {200} | REDIRECT_STATUS_CODES
REDIRECT_CYCLES_LIMIT = 10


class Command(BaseCommand):
    help = "Check for broken links in product fields and update the BrokenLink model."
    product_dict = defaultdict(lambda: defaultdict(list))
    url_set = set()
    url_response_status_codes = defaultdict(int)
    founded_broken_link_ids = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            "-R",
            action="store_true",
            help="Reset all the broken links.",
        )

    def request_head(self, url: str, allow_default_redirects=False, redirect_cycle=0):
        """
        Description
        -----------
        Implementation of `requests.head(url)` that raises a TooManyRedirects error if the redirect_cycle exceeds
        the redirect_cycle_limit and prevent errors in certain special cases:
        - Case 1: Make sure that each URL starts with https if not defined - in some cases url = 'www.url.com'
        - Case 2: Response header location is the same as the original url - use the default allow_redirect behavior.
        - Case 3: Response header location is a relative path - add this path to the previous requested url. (case example: https://lang.com/, https://www.coevorden.nl/afspraak).
        - Case 4: Status code 404 when the request is redirected with the default allow_redirect behavior (case example: https://digid.nl/inloggen).

        Parameters
        ----------
        - url : str
            The requested url
        - allow_redirects : bool, optional
            Boolean indicating if the default allow_redirects method is used.
        - redirect_cycle : int, optional
            The redirect_cycle is used to prevent infinite redirects.
            Some of the requested sites allow an infinite loop of redirects.
            To prevent this the redirect_cycle is used to track the cycles.
            If the cycle exceeds REDIRECT_CYCLES_LIMIT an error can be raised.

        Returns
        -------
        - response : Response
        """
        # Case 1
        if url.startswith((INVALID_URL_ADAPTERS, *VALID_URL_ADAPTERS)):
            url = url
        elif not url.startswith("http"):
            url = f"https://{url}"

        response = requests.head(
            url, timeout=5, allow_redirects=allow_default_redirects
        )

        if response.status_code in REDIRECT_STATUS_CODES:
            redirect_url = url

            if redirect_cycle == REDIRECT_CYCLES_LIMIT:
                raise requests.TooManyRedirects(f"Too many redirects for URL: {url}")

            redirect_cycle += 1
            joined_url = parse.urljoin(url, response.headers["location"])

            # Case 2
            if (
                response.headers["location"] == redirect_url
                or joined_url == redirect_url
            ):
                allow_default_redirects = True
            # Case 3
            elif not response.headers["location"].startswith("http"):
                redirect_url = joined_url
            else:
                # Case 4
                redirect_url = response.headers["location"]

            return self.request_head(
                url=redirect_url,
                allow_default_redirects=allow_default_redirects,
                redirect_cycle=redirect_cycle,
            )

        return response

    def get_products_to_check(self, product: Product):
        localized_product: LocalizedProduct
        for localized_product in product.most_recent_version.vertalingen.all():
            decentrale_field = (None, None)

            def localized_field_verbose_name(field_name: str):
                configured_field_name = getattr(
                    ProductFieldConfiguration.get_solo().localizedproductfieldconfiguration_set.get(
                        taal="nl"
                    ),
                    f"localizedproduct_{field_name}",
                )[0][0]
                return f"{configured_field_name} ({localized_product.taal})"

            for key, value in localized_product.__dict__.items():
                if key in FIELD_NAMES_CONFIG["decentrale_label"]:
                    _, url = decentrale_field
                    if not url:
                        decentrale_field = (value, url)
                        continue

                    self.product_dict[product.pk][
                        f"online aanvragen ({localized_product.taal})"
                    ].append((value, url))
                    self.url_set.add(url)

                elif key in FIELD_NAMES_CONFIG["decentrale_link"]:
                    label, _ = decentrale_field
                    if not label:
                        decentrale_field = (label, value)
                        continue

                    self.product_dict[product.pk][
                        f"online aanvragen ({localized_product.taal})"
                    ].append((label, value))
                    self.url_set.add(value)

                if not value:
                    continue

                if key in FIELD_NAMES_CONFIG["markdown_fields"]:
                    occurring_field = localized_field_verbose_name(key)
                    html = markdown.markdown(value)
                    soup = BeautifulSoup(html, "html.parser")
                    for link in soup.find_all("a"):
                        text = link.get_text()  # Get the label, request VNG.
                        href = link["href"]
                        self.product_dict[product.pk][occurring_field].append(
                            (text, href)
                        )
                        self.url_set.add(href)

                elif key in FIELD_NAMES_CONFIG["urls_fields"]:
                    occurring_field = localized_field_verbose_name(key)
                    for label, url in value:
                        self.product_dict[product.pk][occurring_field].append(
                            (label, url)
                        )
                        self.url_set.add(url)

    def check_url(self, url: str):
        try:
            response = self.request_head(url=url)
            response.close()
            return (url, response.status_code)
        except requests.exceptions.InvalidSchema:
            # These adapters will work most likely in the front-end, but the back-end will not know.
            if url.startswith(VALID_URL_ADAPTERS):
                return (url, SUCCES_STATUS_CODE)
            # Exception for URLs starting with ['tel:', 'sms:', 'geo:', ...]
            return (url, ANY_ERROR_STATUS_CODE)
        except requests.RequestException:
            return (url, ANY_ERROR_STATUS_CODE)

    def handle_response_code(self, url, occurring_field, product_pk, url_label):
        """
        Description
        -----------
        Increment or delete the broken_link based on the status_code

        Parameters
        ----------
        - status_code : int
            The status_code of the response. (most likely 200, 404 or 420).
        - url : str
            The url of the request response.
        - broken_links : BrokenLinks
            The broken link class model that interacts with the DB.
        - url_label : str,
            The 'label' of the url in the content.
        """
        url_status_code = self.url_response_status_codes[url]

        broken_link, _ = BrokenLinks.objects.get_or_create(
            product_id=product_pk,
            url=url,
            occurring_field=occurring_field,
            url_label=url_label,
        )

        if url_status_code in SUCCESSFUL_STATUS_CODES:
            broken_link.delete()
            self.stdout.write(self.style.SUCCESS(f"{url} - [{url_status_code}]"))
        else:
            broken_link.increment_error_count()
            self.founded_broken_link_ids.append(broken_link.id)
            self.stdout.write(self.style.ERROR(f"{url} - [{url_status_code}]"))

    def reset_broken_links(self, reset_all=False):
        """
        Description
        -----------
        Reset and delete every BrokenLink that is indexed in the database, but not in the content.
        Or reset each broken link in the DB.

        Parameters
        ----------
        - reset_all , bool
            Clean all the links or just the excluded ones.
        """
        if reset_all:
            links = BrokenLinks.objects.all()
            for link in links:
                link.reset_error_count()
            return self.stdout.write(
                self.style.SUCCESS(
                    "Successfully cleared the error_count of every BrokenLink."
                )
            )
        else:
            cleanup_objects = BrokenLinks.objects.exclude(
                id__in=self.founded_broken_link_ids
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {cleanup_objects.count()} old BrokenLinks."
                )
            )
            cleanup_objects.delete()

    def handle(self, *args, **options):
        if options.get("reset"):
            self.reset_broken_links(reset_all=True)
            return

        with parallel(max_workers=32) as executor:
            for product in Product.objects.prefetch_related(
                "most_recent_version__vertalingen"
            ).exclude_generic_status()[:100]:
                self.get_products_to_check(product)

            # Map all futures to the executor
            futures = executor.map(self.check_url, self.url_set)

            # Wait for all the futures
            for url, status_code in futures:
                print(url, status_code)
                self.url_response_status_codes[url] = status_code

            data_chain = chain.from_iterable(
                [
                    (
                        (product_pk, field_name, url_label, url_href)
                        for product_pk, product_fields in self.product_dict.items()
                        for field_name, urls in product_fields.items()
                        for url_label, url_href in urls
                    )
                ]
            )

            for product_pk, field_name, url_label, url_href in data_chain:
                self.handle_response_code(
                    url=url_href,
                    occurring_field=field_name,
                    product_pk=product_pk,
                    url_label=url_label,
                )

            self.reset_broken_links()
