from collections import defaultdict
from itertools import chain
from urllib import parse

from django.core.management import BaseCommand

import markdown
import requests
import urllib3
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from zgw_consumers.concurrent import parallel

from sdg.core.models import ProductFieldConfiguration
from sdg.producten.models import BrokenLinks, Product

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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


class Command(BaseCommand):
    help = "Check for broken links in product fields and update the BrokenLink model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            "-R",
            action="store_true",
            help="Reset all the broken links.",
        )

    def create_session(self):
        """
        Create a requests session with retry capabilities and custom headers
        """
        session = requests.Session()

        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        # Set custom headers to mimic a browser
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "nl,en-US;q=0.7,en;q=0.3",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
            }
        )

        return session

    def request_head(self, session, url: str):
        """
        Implementation of `requests.head(url)` with improved error handling
        and support for sites that don't properly implement HEAD.

        :param session: requests.Session to use for the request
        :param url: The requested url
        :param timeout: Timeout in seconds
        :returns: Response object and error message if any
        """
        # Normalize URL
        if url.startswith((INVALID_URL_ADAPTERS, *VALID_URL_ADAPTERS)):
            parsed_url = url
        elif not url.startswith("http"):
            parsed_url = f"https://{url}"
        else:
            parsed_url = url

        try:
            # Use GET with stream=True to avoid downloading the entire content
            response = session.get(
                parsed_url,
                timeout=20,
                stream=True,
                allow_redirects=True,
                verify=False,
            )
            # Close connection to avoid downloading entire content
            response.close()
            return response, None

        except Exception as e:
            return None, str(e)

    def check_url_with_retry(self, url: str):
        """
        Check a url with retry mechanism and return a tuple of the url and status_code

        :param url: The url to check
        :param max_retries: Maximum number of retries
        :param timeout: Request timeout in seconds
        :returns: (url, status_code, message) The checked url, response status code, and error message if any
        """

        # Check for special URL schemes
        if url.startswith(VALID_URL_ADAPTERS):
            return (url, SUCCES_STATUS_CODE, None)

        if url.startswith(INVALID_URL_ADAPTERS):
            return (url, ANY_ERROR_STATUS_CODE, "Invalid URL scheme")

        # Create a new session for each URL to avoid cookie/session contamination
        session = self.create_session()

        # for attempt in range(max_retries + 1):
        try:
            response, error_msg = self.request_head(session, url)

            if response:
                status_code = response.status_code
                # Check for false 200 responses (some servers return 200 for missing pages)
                if status_code == 200 and len(response.content) < 100:
                    # If the page is suspiciously small, it might be a custom error page
                    if (
                        b"not found" in response.content.lower()
                        or b"404" in response.content
                    ):
                        status_code = 404
                return (url, status_code, None)
            else:
                # If this is the last attempt, return error
                return (url, ANY_ERROR_STATUS_CODE, error_msg)

        except Exception as e:
            # If this is the last attempt, return error
            error_msg = str(e)
            return (url, ANY_ERROR_STATUS_CODE, error_msg)

    def handle_response_code(
        self,
        url,
        occurring_field,
        product_pk,
        url_label,
        founded_status_code,
        founded_broken_link_ids,
    ):
        """
        Increment or delete the broken_link based on the status_code

        :param url: The url of the request response.
        :param occurring_field: The field where the URL was found
        :param product_pk: The primary key of the product
        :param url_label: The 'label' of the url in the content.
        :param founded_status_code: The response status code of the requested url
        :param error_message: Any error message from the request
        :param founded_broken_link_ids: A list containing all the checked ids
        """
        broken_link, _ = BrokenLinks.objects.get_or_create(
            product_id=product_pk,
            url=url[:2000],
            occurring_field=occurring_field,
            url_label=url_label,
        )

        # Good status - delete broken link entry
        if founded_status_code not in [404, 420]:
            broken_link.delete()

        # Definitely broken
        else:
            broken_link.increment_error_count()
            broken_link.save()
            founded_broken_link_ids.append(broken_link.id)

    def reset_broken_links(self, founded_broken_link_ids=[], reset_all=False):
        """
        Reset and delete every BrokenLink that is indexed in the database, but not in the content.
        Or reset each broken link in the DB.

        :param founded_broken_link_ids: A list containing all the checked ids (each broken link that is not in this list will be removed).
        :param reset_all: Clean all the links or just the excluded ones.
        """
        if reset_all:
            links = BrokenLinks.objects.all()
            for link in links:
                link.reset_error_count()

            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully cleared the error_count of every BrokenLink."
                )
            )
        else:
            # Delete links that are no longer broken or don't exist anymore
            cleanup_objects = BrokenLinks.objects.exclude(
                id__in=founded_broken_link_ids
            )
            total = cleanup_objects.count()
            cleanup_objects.delete()

            self.stdout.write(self.style.SUCCESS(f"Deleted {total} old BrokenLinks."))

    def is_valid_url(self, url: str):
        """
        Perform additional validation before checking a URL.

        :param url: URL to validate
        :returns: Boolean indicating if URL is valid
        """
        # Skip empty URLs
        if not url or url.strip() == "":
            return False

        # Skip fragment-only URLs
        if url.startswith("#"):
            return False

        # Skip JavaScript URLs
        if url.startswith("javascript:"):
            return False

        # Check for valid scheme
        parsed = parse.urlparse(url)
        if not parsed.scheme and not url.startswith(("www.", *VALID_URL_ADAPTERS)):
            if not parsed.netloc and parsed.path:
                # This might be a relative URL - keep it for checking
                return True
            return False

        return True

    def get_url_set(self, products: Product):
        decentrale_field = (None, None)
        url_set = set()
        product_dict = defaultdict(lambda: defaultdict(list))

        # Def helper function.
        def localized_field_verbose_name(field_name: str, taal: str):
            configured_field_name = getattr(
                ProductFieldConfiguration.get_solo().localizedproductfieldconfiguration_set.get(
                    taal="nl"
                ),
                f"localizedproduct_{field_name}",
            )[0][0]
            return f"{configured_field_name} ({taal})"

        for product in products:
            for localized_product in product.most_recent_version.vertalingen.all():
                for key, value in localized_product.__dict__.items():
                    if key in FIELD_NAMES_CONFIG["decentrale_label"]:
                        _, url = decentrale_field
                        if not url:
                            decentrale_field = (value, url)
                            continue

                        if self.is_valid_url(url):
                            product_dict[product.pk][
                                f"online aanvragen ({localized_product.taal})"
                            ].append((value, url))
                            url_set.add(url)

                    elif key in FIELD_NAMES_CONFIG["decentrale_link"]:
                        label, _ = decentrale_field
                        if not label:
                            decentrale_field = (label, value)
                            continue

                        if self.is_valid_url(url):

                            product_dict[product.pk][
                                f"online aanvragen ({localized_product.taal})"
                            ].append((label, value))
                            url_set.add(value)

                    if not value:
                        continue

                    if key in FIELD_NAMES_CONFIG["markdown_fields"]:
                        occurring_field = localized_field_verbose_name(
                            key, localized_product.taal
                        )
                        html = markdown.markdown(value)
                        soup = BeautifulSoup(html, "html.parser")
                        for link in soup.find_all("a"):
                            text = link.get_text()  # Get the label, request VNG.
                            href = link.get("href", "")
                            if self.is_valid_url(url):
                                product_dict[product.pk][occurring_field].append(
                                    (text, href)
                                )
                                url_set.add(href)

                    elif key in FIELD_NAMES_CONFIG["urls_fields"]:
                        occurring_field = localized_field_verbose_name(
                            key, localized_product.taal
                        )
                        for label, url in value:
                            if self.is_valid_url(url):
                                product_dict[product.pk][occurring_field].append(
                                    (label, url)
                                )
                                url_set.add(url)

        return (url_set, product_dict)

    def handle(self, **options):
        # Handle Reset
        if options.get("reset"):
            self.reset_broken_links(reset_all=True)
            return

        # Storage
        founded_broken_link_ids = []
        url_response_dict = defaultdict(tuple)

        # Get all products
        products = Product.objects.prefetch_related(
            "most_recent_version__vertalingen"
        ).exclude_generic_status()

        (url_set, product_dict) = self.get_url_set(products)

        url_list = list(url_set)

        with parallel() as executor:
            # Map all futures to the executor
            futures = executor.map(self.check_url_with_retry, url_list)

            # Process results
            for url, status_code, error_msg in futures:
                url_response_dict[url] = (status_code, error_msg)

        data_chain = chain.from_iterable(
            [
                (
                    (product_pk, field_name, url_label, url_href)
                    for product_pk, product_fields in product_dict.items()
                    for field_name, urls in product_fields.items()
                    for url_label, url_href in urls
                )
            ]
        )

        for product_pk, field_name, url_label, url_href in data_chain:
            status_code, error_msg = url_response_dict.get(
                url_href, (ANY_ERROR_STATUS_CODE, "URL not checked")
            )
            self.handle_response_code(
                url=url_href,
                occurring_field=field_name,
                product_pk=product_pk,
                url_label=url_label,
                founded_status_code=status_code,
                founded_broken_link_ids=founded_broken_link_ids,
            )

        self.reset_broken_links(founded_broken_link_ids=founded_broken_link_ids)
