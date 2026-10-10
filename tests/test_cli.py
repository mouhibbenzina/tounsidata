import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tounsidata import cli
from tounsidata.client import CatalogError


class FakeResponse:
    def __init__(self, content: bytes):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self.content


class CliTests(unittest.TestCase):
    @patch("tounsidata.cli.CatalogClient")
    def test_json_search_escapes_unicode_for_windows_consoles(self, client_class):
        client_class.return_value.search.return_value = [{"title": "بيانات مفتوحة"}]
        output = io.StringIO()

        with patch("tounsidata.cli.sys.stdout", output):
            result = cli.main(["search", "data", "--json"])

        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output.getvalue()), [{"title": "بيانات مفتوحة"}])
        self.assertIn("\\u", output.getvalue())

    @patch("tounsidata.cli._download_ssl_context")
    @patch("tounsidata.cli.urlopen")
    def test_download_writes_resource_and_uses_ssl_context(self, urlopen, ssl_context):
        urlopen.return_value = FakeResponse(b"date,temperature\n2024-01-01,18\n")
        dataset = {
            "resources": [
                {"id": "resource-1", "url": "https://example.test/data.csv", "name": "climate.csv"}
            ]
        }
        ssl_context.return_value = object()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "data.csv"

            cli._download(dataset, None, output)

            self.assertEqual(output.read_bytes(), b"date,temperature\n2024-01-01,18\n")
        self.assertEqual(urlopen.call_args.kwargs["context"], ssl_context.return_value)

    def test_download_rejects_missing_resource_id(self):
        with self.assertRaisesRegex(CatalogError, "no downloadable resources"):
            cli._download({"resources": []}, None, Path("unused.csv"))


if __name__ == "__main__":
    unittest.main()
