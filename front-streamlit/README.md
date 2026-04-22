# Front Streamlit

## Installation

1. Go to the frontend folder:

   cd front-streamlit

2. Install dependencies with Poetry:

   poetry install

## Run dashboard

1. Start FastAPI first (port 8890 by default).
2. Start Streamlit from this folder:

   poetry run streamlit run dashboard/Accueil_des_dashboards.py

The dashboard includes an environment page with a hybrid data strategy: hourly meteo_by_city remains on silver, the daily air_quality_by_city summary uses gold, and the ATMO map keeps the detailed silver layer.

No FASTAPI_BASE_URL is required on the command line when FastAPI runs on http://localhost:8890.

## Optional custom API URL

You can configure a different API URL once with an environment variable in a .env file.

Example in repository .env or front-streamlit/.env:

FASTAPI_BASE_URL=http://localhost:8890
FASTAPI_TIMEOUT_SECONDS=25
FASTAPI_PAGE_LIMIT=1000

If FastAPI protection is enabled, add the same API key on the frontend side:

FASTAPI_API_KEY=super-secret
FASTAPI_API_KEY_HEADER=X-API-Key
