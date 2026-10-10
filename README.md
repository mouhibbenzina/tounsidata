# TounsiData

A lightweight, open-source Python CLI for exploring Tunisia's national open-data catalog. It uses the catalog's public CKAN API and requires no runtime dependencies beyond Python 3.10+.

> TounsiData is an independent community project, not an official government service. Dataset availability, quality, reuse rights, and freshness are determined by each publisher. Check a dataset's license and metadata before using it.

## Quick start

```bash
python -m pip install .
tounsidata search emploi
tounsidata show donnees-climatiques-station-weslatia-dgacta
```

Search by French, Arabic, or other catalog terms:

```bash
tounsidata search "transport" --limit 5
tounsidata search "بطالة" --json
```

Search results show the dataset ID to pass to `show` or `download`. Replace example values such as `DATASET_ID` with an actual ID from your search results; typing the placeholder literally will not work. For example:

```bash
tounsidata download donnees-climatiques-station-weslatia-dgacta --output data/climat.csv
```

`show` prints complete metadata, including publisher, license, descriptions, and resource links. For a dataset with multiple resources, use `--resource RESOURCE_ID` with `download`; otherwise the first downloadable resource is used.

## Development

```bash
python -m unittest discover -s tests -v
python -m tounsidata.cli --help
```

No third-party runtime packages are required. To test against another CKAN instance, pass its Action API URL:

```bash
tounsidata --api-url https://catalog.data.gov.tn/api/3/action search agriculture
```

## Try every CLI scenario (Windows PowerShell)

Run these commands from the cloned `tounsidata` repository folder. Install the current checkout, then run the automated tests:

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
```

Try a live search, JSON output, and an intentional no-results search:

```powershell
tounsidata search climat --limit 3
tounsidata search climat --limit 2 --json
tounsidata search no-such-tounsidata-query-987654 --limit 2
```

Copy an ID from the search output, then inspect and download that dataset:

```powershell
$dataset = "donnees-climatiques-station-weslatia-dgacta"
tounsidata show $dataset
New-Item -ItemType Directory -Force data | Out-Null
tounsidata download $dataset --output data\climat.csv
Get-Item data\climat.csv
```

To exercise resource selection, find a resource `id` in `tounsidata show $dataset` and pass it to `--resource RESOURCE_ID`. The first downloadable resource is selected when `--resource` is omitted.

These commands intentionally return errors: the first explains that `DATASET_ID` is only a placeholder, and the second rejects a limit outside 1–100.

```powershell
tounsidata show DATASET_ID
tounsidata search climat --limit 0
```

## Data source

The default endpoint is the public [CKAN Action API](https://catalog.data.gov.tn/api/3/action) for Tunisia's [national open-data catalog](https://data.gov.tn/). TounsiData fetches catalog metadata and resource URLs; it does not mirror or modify the published datasets.

## Contributing

Issues and pull requests are welcome. Useful first contributions include Arabic/French documentation improvements, tests for additional CKAN response shapes, and small examples using datasets whose licenses permit reuse. Please include the catalog dataset URL and license when proposing a dataset-based example. Avoid committing downloaded personal or sensitive data.

## License

MIT. This license applies to TounsiData's code, not to datasets hosted by the catalog.
