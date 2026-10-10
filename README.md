# TounsiData

A lightweight, open-source Python CLI for exploring Tunisia's national open-data catalog. It uses the catalog's public CKAN API and requires no runtime dependencies beyond Python 3.10+.

> TounsiData is an independent community project, not an official government service. Dataset availability, quality, reuse rights, and freshness are determined by each publisher. Check a dataset's license and metadata before using it.

## Quick start

```bash
python -m pip install .
tounsidata search emploi
tounsidata show DATASET_ID
tounsidata download DATASET_ID --output data/dataset.csv
```

Search by French, Arabic, or other catalog terms:

```bash
tounsidata search "transport" --limit 5
tounsidata search "بطالة" --json
```

Search results show the catalog dataset name as its ID. `show` prints complete metadata, including publisher, license, descriptions, and resource links. For a dataset with multiple resources, use `--resource RESOURCE_ID` with `download`; otherwise the first downloadable resource is used.

## Development

```bash
python -m unittest discover -s tests -v
python -m tounsidata.cli --help
```

No third-party runtime packages are required. To test against another CKAN instance, pass its Action API URL:

```bash
tounsidata --api-url https://catalog.data.gov.tn/api/3/action search agriculture
```

## Data source

The default endpoint is the public [CKAN Action API](https://catalog.data.gov.tn/api/3/action) for Tunisia's [national open-data catalog](https://data.gov.tn/). TounsiData fetches catalog metadata and resource URLs; it does not mirror or modify the published datasets.

## Contributing

Issues and pull requests are welcome. Useful first contributions include Arabic/French documentation improvements, tests for additional CKAN response shapes, and small examples using datasets whose licenses permit reuse. Please include the catalog dataset URL and license when proposing a dataset-based example. Avoid committing downloaded personal or sensitive data.

## License

MIT. This license applies to TounsiData's code, not to datasets hosted by the catalog.
