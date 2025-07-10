import logging
from io import StringIO
from pathlib import Path
from typing import IO, Optional
from urllib.parse import urljoin

import requests
import yaml
from zgw_consumers.models import Service

logger = logging.getLogger(__name__)


class SDGClient:
    def __init__(
        self,
        auth_value: Optional[dict[str, str]] = None,
        schema_url: str = "",
        schema_file: IO = None,
        client_certificate_path=None,
        client_private_key_path=None,
        server_certificate_path=None,
    ):

        self.auth_value = auth_value
        self.schema_url = schema_url
        self.schema_file = schema_file
        self.client_certificate_path = client_certificate_path
        self.client_private_key_path = client_private_key_path
        self.server_certificate_path = server_certificate_path

    SDG_service = Service.objects.get(
        api_root="https://sdgapi.ondernemersplein.overheid.nl/api/v1/"
    )
    default_schema = (
        Path(__file__).parent / "data" / "default_schema.json"
    ).read_text()

    def load_schema_file(file: IO):
        spec = yaml.safe_load(file)
        return spec

    def fetch(self, url: str, *args, **kwargs) -> dict:
        response = requests.get(url, *args, **kwargs)
        response.raise_for_status()

        spec = yaml.safe_load(response.content)
        spec_version = response.headers.get(
            "X-OAS-Version", spec.get("openapi", spec.get("swagger", ""))
        )
        if not spec_version.startswith("3.0"):
            raise ValueError("Unsupported spec version: {}".format(spec_version))

        return spec

    def fetch_schema(self) -> None:
        """
        Override the default fetch_schema method to add missing operation ids.
        """
        try:
            if self.schema_file:
                logger.info("Loaded schema from file '%s'", self.schema_file)
                self._schema = self.load_schema_file(self.schema_file)
            else:
                url = self.schema_url or urljoin(
                    self.SDG_service.api_root, "schema/openapi.yaml"
                )
                logger.info("Fetching schema at '%s'", url)
                self._schema = self.fetch(url, {"v": "3"})
        except requests.HTTPError:
            schema = self.default_schema.replace("{{products_url}}", self.products_url)
            self._schema = self.load_schema_file(StringIO(schema))

        self.paths = self._schema["paths"]
        self.paths[self.products_url]["get"]["operationId"] = "productenList"
        self.paths[f"{self.products_url}/{{id}}"]["get"][
            "operationId"
        ] = "productenRetrieve"

    @property
    def products_url(self):
        return urljoin(self.SDG_service.api_root, "producten")

    def retrieve_products(self):
        response = {"next": self.products_url}
        results = []
        while response.get("next"):
            try:
                response = requests.get(response["next"], "productenList")
                response = response.json()
                results.extend(response["results"])
            except ConnectionError:
                break
        return results
