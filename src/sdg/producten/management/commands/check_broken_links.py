from collections import defaultdict
from collections.abc import Sequence
from typing import TypedDict
from urllib import parse

from django.core.management import BaseCommand

import markdown
import requests
import urllib3
from bs4 import BeautifulSoup
from glom import glom
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from zgw_consumers.concurrent import parallel

from sdg.core.models import ProductFieldConfiguration
from sdg.producten.models import BrokenLinks, Product

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MARKDOWN_LINKS = [
    "specifieke_tekst",
    "vereisten",
    "bewijs",
    "procedure_beschrijving",
    "kosten_en_betaalmethoden",
    "uiterste_termijn",
    "bezwaar_en_beroep",
    "wtd_bij_geen_reactie",
]

VALID_URL_ADAPTERS = ("tel:", "sms:", "mailto:")
INVALID_URL_ADAPTERS = "geo:"
SUCCES_STATUS_CODE = 200
ANY_ERROR_STATUS_CODE = 420


class FieldUrl(TypedDict):
    field: str
    label: str
    url: str


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
    ) -> int | None:
        """
        Increment or delete the broken_link based on the status_code

        :param url: The url of the request response.
        :param occurring_field: The field where the URL was found
        :param product_pk: The primary key of the product
        :param url_label: The 'label' of the url in the content.
        :param founded_status_code: The response status code of the requested url
        :param error_message: Any error message from the request
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
            return

        # Definitely broken
        broken_link.increment_error_count()
        broken_link.save()
        return broken_link.id

    def reset_broken_links(self, ignore_broken_ids=list, reset_all=False):
        """
        Reset and delete every BrokenLink that is indexed in the database, but not in the content.
        Or reset each broken link in the DB.

        :param ignore_broken_ids: A list containing all the ids which we don't want to reset.
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
            cleanup_objects = BrokenLinks.objects.exclude(id__in=ignore_broken_ids)
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

    def localized_field_verbose_name(self, field_name: str, taal: str):
        if configured_field_name := getattr(
            ProductFieldConfiguration.get_solo().localizedproductfieldconfiguration_set.get(
                taal=taal
            ),
            f"localizedproduct_{field_name}",
        ):
            field_name = configured_field_name[0][0]

        return f"{field_name} ({taal})"

    def get_product_urls(self, products: Sequence[Product]):
        product_dict = defaultdict(list)

        for product in products:
            for localized_product in product.most_recent_version.vertalingen.all():
                for markdown_field in MARKDOWN_LINKS:
                    occurring_field = self.localized_field_verbose_name(
                        markdown_field, localized_product.taal
                    )
                    value = getattr(localized_product, markdown_field)
                    html = markdown.markdown(value)
                    soup = BeautifulSoup(html, "html.parser")
                    for link in soup.find_all("a"):
                        text = link.get_text()  # Get the label, request VNG.
                        href = link.get("href", "")
                        if self.is_valid_url(href):
                            product_dict[product.id].append(
                                FieldUrl(field=occurring_field, label=text, url=text)
                            )

                if self.is_valid_url(localized_product.decentrale_procedure_link):
                    occurring_field = self.localized_field_verbose_name(
                        "decentrale_procedure_link", localized_product.taal
                    )
                    product_dict[product.id].append(
                        FieldUrl(
                            field=occurring_field,
                            label=localized_product.decentrale_procedure_label,
                            url=localized_product.decentrale_procedure_link,
                        )
                    )

                if verwijzing_links := localized_product.verwijzing_links:
                    occurring_field = self.localized_field_verbose_name(
                        "verwijzing_links", localized_product.taal
                    )
                    for label, url in verwijzing_links:
                        if self.is_valid_url(url):
                            product_dict[product.id].append(
                                FieldUrl(field=occurring_field, label=label, url=url)
                            )

        return product_dict

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

        product_urls: dict[int : list[FieldUrl]] = dict(self.get_product_urls(products))

        with parallel() as executor:
            # create a set of unique urls from the product_urls
            unique_urls = set(glom(product_urls, "**.url"))
            futures = executor.map(self.check_url_with_retry, unique_urls)

            for url, status_code, error_msg in futures:
                url_response_dict[url] = (status_code, error_msg)

        for product_id, url_information_list in product_urls.items():
            for url_information in url_information_list:
                url = url_information["url"]
                status_code, _ = url_response_dict[url]

                if broken_link_id := self.handle_response_code(
                    url=url,
                    occurring_field=url_information["field"],
                    product_pk=product_id,
                    url_label=url_information["label"],
                    founded_status_code=status_code,
                ):
                    founded_broken_link_ids.append(broken_link_id)

        self.reset_broken_links(ignore_broken_ids=founded_broken_link_ids)
