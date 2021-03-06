from zgw_consumers.client import ZGWClient


class SDGClient(ZGWClient):
    def fetch_schema(self) -> None:
        """
        Override the default fetch_schema method to add missing operation ids.
        """
        super().fetch_schema()
        paths = self._schema["paths"]
        paths[self.products_url]["get"]["operationId"] = "productenList"
        paths[f"{self.products_url}/{{id}}"]["get"]["operationId"] = "productenRetrieve"

    @property
    def products_url(self):
        return "/api/v1/producten"

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
