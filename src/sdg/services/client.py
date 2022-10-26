from io import StringIO
from pathlib import Path
from urllib.parse import urljoin

from requests import HTTPError
from zgw_consumers.client import ZGWClient, load_schema_file


class SDGClient(ZGWClient):
    default_schema = (
        Path(__file__).parent / "data" / "default_schema.json"
    ).read_text()

    def fetch_schema(self) -> None:
        """
        Override the default fetch_schema method to add missing operation ids.
        """
        try:
            super().fetch_schema()
        except HTTPError:
            schema = self.default_schema.replace("{{products_url}}", self.products_url)
            self._schema = load_schema_file(StringIO(schema))

        paths = self._schema["paths"]
        paths[self.products_url]["get"]["operationId"] = "productenList"
        paths[f"{self.products_url}/{{id}}"]["get"]["operationId"] = "productenRetrieve"

    @property
    def products_url(self):
        return urljoin(self.base_path, "producten")

    def retrieve_products(self):
        response = {"next": self.products_url}
        results = []
        while response.get("next"):
            try:
                response = self.retrieve("productenList", response["next"])
                results.extend(response["results"])
            except ConnectionError:
                break
        return results
