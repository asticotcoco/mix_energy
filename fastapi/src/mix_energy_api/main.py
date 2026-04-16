from __future__ import annotations

import json
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from .bigquery_service import (
    BigQueryDatasetService,
    BigQueryServiceError,
    InvalidFilterError,
    UnknownColumnError,
    UnknownTableError,
)
from .config import load_settings
from .schemas import DatasetLayer, DatasetOverview, FilterClause, QueryResponse, TableColumns

from predict.train import predict_conso


def _parse_columns(columns: str | None) -> list[str] | None:
    if not columns:
        return None
    if columns.strip() == "*":
        return None
    parsed_columns = [column.strip() for column in columns.split(",") if column.strip()]
    return parsed_columns or None


def _parse_filters(filters: str | None) -> list[FilterClause] | None:
    if not filters:
        return None

    try:
        payload = json.loads(filters)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400, detail="filters must be valid JSON"
        ) from exc

    if not isinstance(payload, list):
        raise HTTPException(status_code=400, detail="filters must be a JSON array")

    try:
        return [FilterClause.model_validate(item) for item in payload]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def create_app() -> FastAPI:
    settings = load_settings()
    app = FastAPI(
        title="Mix Energy Dataset API",
        version="0.1.0",
        description="Read-only BigQuery buffer for the Streamlit front-end.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _startup() -> None:
        app.state.settings = settings
        services: dict[str, BigQueryDatasetService] = {}
        for layer in ("raw", "silver", "gold"):
            layer_settings = settings.__class__(
                project_id=settings.project_id,
                dataset_base=settings.dataset_base,
                dataset_id=settings.dataset_id_for_layer(layer),
                credentials_path=settings.credentials_path,
                default_limit=settings.default_limit,
                max_limit=settings.max_limit,
                default_layer=settings.default_layer,
                allowed_origins=settings.allowed_origins,
                include_hidden_tables=settings.include_hidden_tables,
            )
            services[layer] = BigQueryDatasetService.create(layer_settings)

        app.state.services = services

    def get_service(request: Request, layer: DatasetLayer = "gold") -> BigQueryDatasetService:
        services = getattr(request.app.state, "services", None)
        if services is None:
            raise HTTPException(status_code=503, detail="BigQuery services are not ready")
        service = services.get(layer)
        if service is None:
            raise HTTPException(status_code=404, detail=f"Dataset layer '{layer}' is not available")
        return service

    @app.get("/health")
    def health(request: Request, layer: DatasetLayer = Query(default="gold")) -> dict[str, str]:
        service = get_service(request, layer=layer)
        return {
            "status": "ok",
            "project_id": service.settings.project_id,
            "dataset_id": service.settings.dataset_id,
            "layer": layer,
        }

    @app.get("/tables", response_model=DatasetOverview)
    def list_tables(
        request: Request,
        layer: DatasetLayer = Query(default="gold"),
    ) -> dict[str, Any]:
        service = get_service(request, layer=layer)
        service.refresh_tables()
        return {
            "project_id": service.settings.project_id,
            "dataset_id": service.settings.dataset_id,
            "tables": service.list_tables(),
        }

    @app.get("/tables/{table_name}/columns", response_model=TableColumns)
    def get_table_columns(
        request: Request,
        table_name: str,
        layer: DatasetLayer = Query(default="gold"),
    ) -> dict[str, Any]:
        service = get_service(request, layer=layer)
        try:
            columns = service.get_table_columns(table_name)
            return {
                "table_name": table_name,
                "columns": columns,
            }
        except UnknownTableError as exc:
            service.refresh_tables()
            try:
                columns = service.get_table_columns(table_name)
                return {
                    "table_name": table_name,
                    "columns": columns,
                }
            except UnknownTableError:
                pass
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/tables/{table_name}", response_model=QueryResponse)
    def query_table(
        request: Request,
        table_name: str,
        columns: str | None = Query(
            default=None, description="Comma-separated list of columns"
        ),
        filters: str | None = Query(
            default=None,
            description="JSON array of filter clauses, e.g. [{'field':'date','operator':'gte','value':'2024-01-01'}]",
        ),
        layer: DatasetLayer = Query(default="gold"),
        limit: int | None = Query(default=None, ge=1),
    ) -> dict[str, Any]:
        service = get_service(request, layer=layer)
        parsed_columns = _parse_columns(columns)
        parsed_filters = _parse_filters(filters)

        try:
            return service.query_table(
                table_name,
                columns=parsed_columns,
                filters=parsed_filters,
                limit=limit,
            )
        except UnknownTableError as exc:
            service.refresh_tables()
            try:
                return service.query_table(
                    table_name,
                    columns=parsed_columns,
                    filters=parsed_filters,
                    limit=limit,
                )
            except UnknownTableError:
                pass
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except UnknownColumnError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except InvalidFilterError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except BigQueryServiceError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/predict/national")
    def predict_nat(request: Request):
        service = get_service(request, layer="gold")
        predicted_val = predict_conso(service.client, True)
        if predicted_val is None:
            raise HTTPException(
                status_code=204, detail=str("No sufficient data for the prediction")
            )

        return predicted_val

    @app.post("/predict/region")
    def predict_region(
        request: Request,
        code_insee_region: int,
    ):
        service = get_service(request, layer="gold")
        predicted_val = predict_conso(service.client, False, code_insee_region)
        if predicted_val is None:
            raise HTTPException(
                status_code=204, detail=str("No sufficient data for the prediction")
            )

        return predicted_val

    return app


app = create_app()
