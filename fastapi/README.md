# FastAPI service

Read-only API for the Mix Energy BigQuery dataset.

## Run locally

Use the repository Python environment. The API loads the repository `.env` automatically via `python-dotenv`, and imports the shared `predict` package from the repository, so the local Python path must include both `fastapi/src` and `predict/src`.

```bash
cd ..
source .venv/bin/activate
PYTHONPATH=fastapi/src:predict/src python -m uvicorn mix_energy_api.main:app --reload --host 0.0.0.0 --port 8890
```

Equivalent Make target:

```bash
make start_fastapi
```

This Make target uses the repository virtual environment directly, so it does not depend on manual shell activation.

The service reads:
- `PROJECT_ID`
- `DATASET_ID_PROD` by default, falling back to `DATASET_ID_DEV`
- `GOOGLE_APPLICATION_CREDENTIALS`, or `GOOGLE_APPLICATION_CREDENTIALS_CONTAINER` if the first one is not set
- `MLFLOW_TRACKING_URI`, by default use 'http:\\\\localhost:8503'
- `FASTAPI_API_KEY` to protect dataset and prediction endpoints with an API key
- `FASTAPI_API_KEY_HEADER`, default `X-API-Key`

## Query pattern

- `GET /tables` lists all table names in the gold dataset.
- `GET /tables/{table_name}/columns` returns the list of columns for a specific table.
- `GET /tables/{table_name}` queries a table with optional `columns`, `filters`, and `limit` query parameters.
- The optional `layer` query parameter accepts `raw`, `silver`, or `gold` and defaults to `gold`.
- `POST /predict/national` ask for a prediction of the national energy consumption of the next 15 minutes
- `POST /predict/region` ask for a prediction of the energy consumption of the next 15 minutes of a specific France region

Example URLs:

```bash
curl http://localhost:8890/tables
curl 'http://localhost:8890/tables?layer=silver'
curl http://localhost:8890/tables/kpi/columns
curl 'http://localhost:8890/tables/meteo_by_city/columns?layer=silver'
curl 'http://localhost:8890/tables/nat_cons_agre_j?columns=*' # All columns
curl 'http://localhost:8890/tables/air_quality_by_city?layer=silver&limit=10'
curl 'http://localhost:8890/tables/nat_cons_agre_j?columns=date,region&filters=[{"field":"region","operator":"eq","value":"FR"}]&limit=10'
curl -X 'POST' 'http://localhost:8890/predict/national' -H 'accept: application/json' -d ''
curl -X 'POST' 'http://localhost:8890/predict/region?code_insee_region=11' -H 'accept: application/json' -d ''
```

## Optional API key protection

If `FASTAPI_API_KEY` is set, dataset and prediction endpoints require the configured header on each request. The `/health` endpoint remains public for liveness checks.

Example:

```bash
curl -H 'X-API-Key: super-secret' http://localhost:8890/tables
curl -H 'X-API-Key: super-secret' 'http://localhost:8890/tables?layer=silver'
```

The `filters` parameter must be JSON, for example:

```json
[
  {"field": "region", "operator": "eq", "value": "FR"},
  {"field": "day", "operator": "gte", "value": "2024-01-01"}
]
```

## Docker

Build:

```bash
docker build -t mix-energy-fastapi -f fastapi/Dockerfile fastapi
```

Run:

```bash
docker run --rm -p 8890:8890 \
  -e PROJECT_ID=... \
  -e DATASET_ID_PROD=... \
  -e GOOGLE_APPLICATION_CREDENTIALS=/path/in/container/key.json \
  -e MLFLOW_TRACKING_URI=... \
  -v /path/to/key.json:/path/in/container/key.json:ro \
  mix-energy-fastapi
```
