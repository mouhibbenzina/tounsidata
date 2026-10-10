"""Minimal client for the CKAN API used by Tunisia's national data catalog."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_API_URL = "https://catalog.data.gov.tn/api/3/action"


class CatalogError(Exception):
    """Raised when the catalog request fails or returns an invalid response."""


class CatalogClient:
    def __init__(self, base_url: str = DEFAULT_API_URL, timeout: float = 20) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/{action}?{urlencode(params)}"
        request = Request(url, headers={"User-Agent": "TounsiData/0.1.0"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise CatalogError(f"Catalog returned HTTP {exc.code} for {action}.") from exc
        except URLError as exc:
            raise CatalogError(f"Could not reach the catalog: {exc.reason}") from exc
        except (TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise CatalogError(f"Could not read a valid catalog response: {exc}") from exc

        if not isinstance(payload, dict) or payload.get("success") is not True:
            message = payload.get("error", "unknown catalog error") if isinstance(payload, dict) else "invalid response"
            raise CatalogError(f"Catalog API error: {message}")
        result = payload.get("result")
        if not isinstance(result, dict):
            raise CatalogError("Catalog API returned an unexpected response shape.")
        return result

    def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        result = self._get("package_search", {"q": query, "rows": limit})
        datasets = result.get("results")
        if not isinstance(datasets, list):
            raise CatalogError("Catalog search response did not contain a dataset list.")
        return datasets

    def get_dataset(self, identifier: str) -> dict[str, Any]:
        dataset = self._get("package_show", {"id": identifier})
        if not dataset.get("name") and not dataset.get("id"):
            raise CatalogError("Catalog dataset response was empty or malformed.")
        return dataset
