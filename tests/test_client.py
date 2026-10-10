import json
import unittest
from unittest.mock import patch

from tounsidata.client import CatalogClient, CatalogError


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self.payload


class CatalogClientTests(unittest.TestCase):
    @patch("tounsidata.client.urlopen")
    def test_search_uses_ckan_search_and_returns_results(self, urlopen):
        urlopen.return_value = FakeResponse(
            {"success": True, "result": {"results": [{"name": "dataset-1"}]}}
        )
        client = CatalogClient("https://example.test/api/3/action")

        datasets = client.search("emploi", 5)

        self.assertEqual(datasets, [{"name": "dataset-1"}])
        request = urlopen.call_args.args[0]
        self.assertIn("/package_search?", request.full_url)
        self.assertIn("q=emploi", request.full_url)
        self.assertIn("rows=5", request.full_url)

    @patch("tounsidata.client.urlopen")
    def test_get_dataset_rejects_ckan_api_error(self, urlopen):
        urlopen.return_value = FakeResponse(
            {"success": False, "error": {"message": "Not found"}}
        )

        with self.assertRaisesRegex(CatalogError, "Not found"):
            CatalogClient().get_dataset("missing")

    @patch("tounsidata.client.urlopen")
    def test_search_rejects_invalid_result_shape(self, urlopen):
        urlopen.return_value = FakeResponse({"success": True, "result": {"results": None}})

        with self.assertRaisesRegex(CatalogError, "dataset list"):
            CatalogClient().search("test")

    @patch("tounsidata.client.urlopen")
    def test_get_dataset_returns_package_show_result(self, urlopen):
        urlopen.return_value = FakeResponse(
            {"success": True, "result": {"id": "dataset-1", "name": "dataset-1"}}
        )

        dataset = CatalogClient().get_dataset("dataset-1")

        self.assertEqual(dataset["name"], "dataset-1")


if __name__ == "__main__":
    unittest.main()
