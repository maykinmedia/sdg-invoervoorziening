import re
import threading
from collections import defaultdict
from urllib import parse

from django.core.management import BaseCommand

import requests
from zgw_consumers.concurrent import parallel

from sdg.producten.models import BrokenLinks, LocalizedProduct, Product


class Command(BaseCommand):
    help = "Check for broken links in product fields and update the BrokenLink model."
    checked_url_dict = {}
    founded_broken_link_ids = []
    url_conditions = defaultdict(lambda: (threading.Lock(), threading.Condition()))
    url_conditions_lock = threading.Lock()

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            "-R",
            action="store_true",
            help="Reset all the broken links.",
        )

        parser.add_argument(
            "--test",
            "-T",
            action="store_true",
            help="Indicate that this function is used in an unittest",
        )

    def request_head(self, url: str, allow_redirects=False, redirect_cycle=0):
        """
        Description
        -----------
        Implementation of `requests.head(url)` that raises a TooManyRedirects error if the redirect_cycle exceeds
        the redirct_cycle_limit and prevent errors in certain special cases:
        - Case 1: Make sure that each URL starts with https if not defined - in some cases url = 'www.url.com'
        - Case 2: Response header location is the same as the original url - use the default allow_redirect behaviour.
        - Case 3: Response header location is a relative path - add this path to the previous requested url. (case example: https://lang.com/, https://www.coevorden.nl/afspraak).
        - Case 4: Status code 404 when the request is redirected with the default allow_redirect behaviour (case example: https://digid.nl/inloggen).

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
            If the cycle exceeds a set limit an error can be raised.

        Returns
        -------
        - response : Response
        """
        redirct_cycle_limit = 10

        # Case 1
        if not url.startswith("http"):
            url = f"https://{url}"

        response = requests.head(url, timeout=5, allow_redirects=allow_redirects)
        redirect_status_codes = {301, 302, 303, 307, 308}

        if response.status_code in redirect_status_codes:
            redirect_url = url
            force_redirect = False

            if redirect_cycle == redirct_cycle_limit:
                raise requests.TooManyRedirects(f"Too many redirects for URL: {url}")

            # Case 2
            if (
                response.headers["location"] == redirect_url
                or parse.urljoin(url, response.headers["location"]) == redirect_url
            ):
                force_redirect = True
            # Case 3
            elif not response.headers["location"].startswith("http"):
                redirect_url = parse.urljoin(url, response.headers["location"])
            else:
                # Case 4
                redirect_url = response.headers["location"]

            return self.request_head(
                self=self,
                url=redirect_url,
                allow_redirects=force_redirect,
                redirect_cycle=redirect_cycle + 1,
            )

        return response

    def extract_urls(self, value: str | list):
        """
        Description
        -----------
        Extract a set of urls from a string or list with regex.

        Parameters
        ----------
        - value : str | list
            The value to extract urls from.

        Returns
        -------
        - set : set
            Containing the urls present in th checked value.
        """
        # https://stackoverflow.com/questions/520031/whats-the-cleanest-way-to-extract-urls-from-a-string-using-python/28552670#28552670
        URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        url_pattern = re.compile(URL_REGEX)
        extracted_urls = set()

        def extract(value: str | list):
            if isinstance(value, list):
                for list_value in value:
                    extract(list_value)
            elif isinstance(value, str):
                founded_urls = url_pattern.findall(value)
                for url in founded_urls:
                    extracted_urls.add(url)

        extract(value)

        return extracted_urls

    def handle_response_code(
        self, status_code: int, url: str, broken_link: BrokenLinks
    ):
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
        """
        self.checked_url_dict[url] = status_code
        successful_status_codes = {200, 301, 302, 303, 307, 308}

        if status_code in successful_status_codes:
            self.stdout.write(self.style.SUCCESS(f"{url} - [{status_code}]"))
            broken_link.delete()
        else:
            broken_link.increment_error_count()
            self.founded_broken_link_ids.append(broken_link.id)
            self.stdout.write(self.style.ERROR(f"{url} - [{status_code}]"))

    def check_url(self, url, product, occuring_field):
        """
        Description
        -----------
        Logic to check if an URL is valid. Multiple threads can check the same URL, each thread, that is the first to check if an url
        is valid, will lock other threads that are trying to check the same URL. Once the first thread is done checking the other threads that were blocked are
        released (and will take the value out of the `checked_url_dict`, since the URL has already been checked).

        Parameters
        ----------
        - url : str
            The url that needs to be checked.
        - product : Product
            The product where the url is found in
        - occuring_field : str
            The field localized_verbose_name of the product where the url is found in. `verbose name (language)`
        """
        with self.url_conditions_lock:
            url_lock, url_condition = self.url_conditions[url]

        with url_condition:  # Automatically acquires the condition's internal lock
            while url_lock.locked():
                url_condition.wait()  # Wait until notified

            # Lock acquired, proceed with URL check
            url_lock.acquire()

            try:
                status_code_in_checked_url_dict = self.checked_url_dict.get(url)
                broken_link, created = BrokenLinks.objects.get_or_create(
                    product=product, url=url, occuring_field=occuring_field
                )
                if status_code_in_checked_url_dict is None:
                    try:
                        response = self.request_head(url)
                        response.close()
                        self.handle_response_code(
                            response.status_code, url=url, broken_link=broken_link
                        )
                    except requests.RequestException:
                        self.handle_response_code(420, url=url, broken_link=broken_link)
                else:
                    self.handle_response_code(
                        status_code_in_checked_url_dict,
                        url=url,
                        broken_link=broken_link,
                    )
            finally:
                url_lock.release()
                url_condition.notify_all()

        with self.url_conditions_lock:
            if url in self.url_conditions:
                del self.url_conditions[url]

    def clean_up_removed_urls(self):
        """
        Description
        -----------
        Delete every BrokenLink that is indexed in the database, but not in the content.
        """
        cleanup_objects = BrokenLinks.objects.exclude(
            id__in=self.founded_broken_link_ids
        )
        cleanup_objects.delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {cleanup_objects.__len__()} old BrokenLinks.")
        )

    def handle(self, *args, **options):
        self.handle_reset = options.get("reset")

        # Command executed with the argument `--reset` or `-R`.
        if self.handle_reset:
            links = BrokenLinks.objects.all()
            for link in links:
                link.reset_error_count()
            return self.stdout.write(
                self.style.SUCCESS(
                    "Succesfully cleared the error_count of every BrokenLink."
                )
            )
        # Default command executed
        futures = []
        max_workers = 32
        with parallel(max_workers=max_workers) as executor:
            for product in Product.objects.exclude_generic_status().annotate_name():
                latest_product_versions = product.get_latest_versions(quantity=1)

                if len(latest_product_versions) == 0:
                    break

                latest_product_version = product.get_latest_versions(quantity=1)[0]
                localized_products = LocalizedProduct.objects.filter(
                    product_versie=latest_product_version.id
                )

                for prod in localized_products:
                    localized_field_verbose_name = (
                        lambda field_name: f"{prod.__class__._meta.get_field(field_name=field_name).verbose_name} ({prod.taal})"
                    )

                    urls = [
                        (localized_field_verbose_name(key), url)
                        for key, value in prod.__dict__.items()
                        if value
                        and key
                        not in [
                            "_state",
                            "_configuration",
                            "id",
                            "taal",
                            "product_versie_id",
                        ]
                        for url in self.extract_urls(value)
                    ]

                    for field_name, url in urls:
                        future = executor.submit(
                            self.check_url, url, product, field_name
                        )
                        futures.append(future)

            # Wait for all futures to complete
            for future in futures:
                try:
                    future.result()  # Ensures any exceptions are raised
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing URL: {e}"))

        self.clean_up_removed_urls()
