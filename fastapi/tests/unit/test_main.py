from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from mix_energy_api import main
from mix_energy_api.bigquery_service import BigQueryDatasetService
from mix_energy_api.config import Settings


class _FakeService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def refresh_tables(self):
        return None

    def list_tables(self):
        return ["sample_table"]

    def get_table_columns(self, table_name: str):
        return [{"name": "col1", "field_type": "STRING", "mode": "NULLABLE"}]

    def query_table(self, table_name: str, columns=None, filters=None, limit=None):
        return {
            "project_id": self.settings.project_id,
            "dataset_id": self.settings.dataset_id,
            "table_name": table_name,
            "selected_columns": columns or ["col1"],
            "filters": filters or [],
            "limit": limit or 100,
            "row_count": 1,
            "rows": [{"col1": "value"}],
        }


def test_health_and_tables_accept_layer_query(monkeypatch):
    settings = Settings(
        project_id="mix-energie-gcp",
        dataset_base="prod_mix_energie",
        dataset_id="prod_mix_energie_gold",
        credentials_path=Path("/tmp/fake.json"),
    )

    monkeypatch.setattr(main, "load_settings", lambda: settings)
    monkeypatch.setattr(
        BigQueryDatasetService,
        "create",
        lambda service_settings: _FakeService(service_settings),
    )

    app = main.create_app()
    with TestClient(app) as client:
        health_response = client.get("/health", params={"layer": "silver"})
        assert health_response.status_code == 200
        assert health_response.json()["dataset_id"] == "prod_mix_energie_silver"
        assert health_response.json()["layer"] == "silver"

        tables_response = client.get("/tables", params={"layer": "raw"})
        assert tables_response.status_code == 200
        assert tables_response.json()["dataset_id"] == "prod_mix_energie"
        assert tables_response.json()["tables"] == ["sample_table"]