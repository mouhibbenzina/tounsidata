"""Command-line interface for searching and downloading Tunisian open data."""

from __future__ import annotations

import argparse
import json
import ssl
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .client import DEFAULT_API_URL, CatalogClient, CatalogError


def _configure_stdout() -> None:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(errors="backslashreplace")


def _download_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    if hasattr(ssl, "enum_certificates"):
        for certificate, encoding, _trust in ssl.enum_certificates("ROOT"):
            if encoding == "x509_asn":
                context.load_verify_locations(cadata=ssl.DER_cert_to_PEM_cert(certificate))
    return context


def _display_search(datasets: list[dict[str, Any]]) -> None:
    if not datasets:
        print("No datasets found.")
        return
    for index, dataset in enumerate(datasets, start=1):
        organization = dataset.get("organization") or {}
        org_name = organization.get("title") or organization.get("name") or "Unknown organization"
        print(f"{index}. {dataset.get('title') or dataset.get('name', 'Untitled')}")
        print(f"   ID: {dataset.get('name', dataset.get('id', 'unknown'))}")
        print(f"   Organization: {org_name} | Resources: {dataset.get('num_resources', 0)}")
        if dataset.get("notes"):
            print(f"   {dataset['notes'].strip()}")


def _download(dataset: dict[str, Any], resource_id: str | None, output: Path) -> None:
    resources = dataset.get("resources", [])
    if not isinstance(resources, list):
        resources = []
    resource = next(
        (
            item
            for item in resources
            if isinstance(item, dict)
            and item.get("url")
            and (resource_id is None or item.get("id") == resource_id)
        ),
        None,
    )
    if resource is None:
        if resource_id:
            raise CatalogError(f"No downloadable resource with id '{resource_id}' exists in this dataset.")
        raise CatalogError("This dataset has no downloadable resources.")

    request = Request(resource["url"], headers={"User-Agent": "TounsiData/0.1.0"})
    try:
        with urlopen(request, timeout=30, context=_download_ssl_context()) as response:
            content = response.read()
    except HTTPError as exc:
        raise CatalogError(f"Resource download returned HTTP {exc.code}.") from exc
    except URLError as exc:
        if isinstance(exc.reason, ssl.SSLCertVerificationError):
            raise CatalogError(
                "TLS certificate verification failed for this resource. Check your "
                "system date and trusted certificates; certificate verification stays enabled."
            ) from exc
        raise CatalogError(f"Could not download resource: {exc.reason}") from exc
    except TimeoutError as exc:
        raise CatalogError("Resource download timed out.") from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)
    print(f"Downloaded {resource.get('name') or resource.get('id')} to {output} ({len(content)} bytes).")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tounsidata",
        description="Search Tunisia's national open-data catalog and download datasets.",
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"CKAN Action API URL (default: {DEFAULT_API_URL})",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search catalog datasets.")
    search_parser.add_argument("query", help="Words or phrase to search for.")
    search_parser.add_argument("--limit", type=int, default=10, help="Maximum results (default: 10).")
    search_parser.add_argument("--json", action="store_true", help="Print complete results as JSON.")

    show_parser = subparsers.add_parser("show", help="Show complete dataset metadata.")
    show_parser.add_argument("dataset", help="Dataset ID or name from search results.")

    download_parser = subparsers.add_parser("download", help="Download a dataset resource.")
    download_parser.add_argument("dataset", help="Dataset ID or name from search results.")
    download_parser.add_argument("--resource", help="Specific resource ID (default: first downloadable resource).")
    download_parser.add_argument("--output", "-o", type=Path, required=True, help="Path to save the resource.")

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "search" and not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100.")

    client = CatalogClient(args.api_url)
    try:
        if args.command == "search":
            datasets = client.search(args.query, args.limit)
            if args.json:
                print(json.dumps(datasets, ensure_ascii=True, indent=2))
            else:
                _display_search(datasets)
        elif args.command == "show":
            print(json.dumps(client.get_dataset(args.dataset), ensure_ascii=True, indent=2))
        elif args.command == "download":
            _download(client.get_dataset(args.dataset), args.resource, args.output)
    except CatalogError as exc:
        print(f"tounsidata: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"tounsidata: could not write '{args.output}': {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
