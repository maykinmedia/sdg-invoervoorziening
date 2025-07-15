from __future__ import annotations

import logging

import requests
from zgw_consumers.client import build_client
from zgw_consumers.models import Service
from zgw_consumers.nlx import NLXClient

logger = logging.getLogger(__name__)

__all__ = ["get_client"]


def get_client(service: Service) -> SDGClient:
    return build_client(service, client_factory=SDGClient)


class SDGClient(NLXClient):
    def _retrieve_recursive_from_url(self, url, results=None):
        if not results:
            results = []

        if not url:
            return results

        response = self.get(url)
        response.raise_for_status()

        data = response.json()
        results += data["results"]
        return self._retrieve_recursive_from_url(data.get("next"), results)

    def retrieve_products(self) -> list:
        try:
            return self._retrieve_recursive_from_url("producten")
        except requests.RequestException as err:
            logger.error("Something went wrong while retrieving products", err)

        return []
