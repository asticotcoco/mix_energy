from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_CORS_ORIGINS = (
    "http://localhost:8501",
    "http://127.0.0.1:8501",
)
VALID_DATASET_LAYERS = ("raw", "silver", "gold")


def load_environment() -> None:
    repo_root_env = Path(__file__).resolve().parents[3] / ".env"
    if repo_root_env.exists():
        load_dotenv(repo_root_env, override=False)
    load_dotenv(override=False)


@dataclass(frozen=True)
class Settings:
    project_id: str
    dataset_base: str
    dataset_id: str
    credentials_path: Path
    default_limit: int = 100
    max_limit: int = 1000
    default_layer: str = "gold"
    allowed_origins: tuple[str, ...] = field(
        default_factory=lambda: DEFAULT_CORS_ORIGINS
    )
    include_hidden_tables: bool = False

    def dataset_id_for_layer(self, layer: str) -> str:
        normalized_layer = layer.strip().lower()
        if normalized_layer not in VALID_DATASET_LAYERS:
            valid_layers = ", ".join(VALID_DATASET_LAYERS)
            raise ValueError(
                f"Unsupported dataset layer '{layer}'. Expected one of: {valid_layers}"
            )

        if normalized_layer == "raw":
            return self.dataset_base

        return f"{self.dataset_base}_{normalized_layer}"


def _parse_origins(raw_value: str | None) -> tuple[str, ...]:
    if not raw_value:
        return DEFAULT_CORS_ORIGINS
    origins = tuple(origin.strip() for origin in raw_value.split(",") if origin.strip())
    return origins or DEFAULT_CORS_ORIGINS


def load_settings() -> Settings:
    load_environment()

    project_id = os.getenv("PROJECT_ID")
    dataset_id_base = os.getenv("DATASET_ID_PROD") or os.getenv("DATASET_ID_DEV")
    default_layer = os.getenv("FASTAPI_DATASET_LAYER", "gold").strip().lower()
    dataset_id = (
        dataset_id_base if default_layer == "raw" else f"{dataset_id_base}_{default_layer}"
        if dataset_id_base
        else None
    )
    credentials_value = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_value:
        credentials_value = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_CONTAINER")

    if not project_id:
        raise ValueError("PROJECT_ID is missing from the environment")
    if not dataset_id:
        raise ValueError(
            "DATASET_ID_PROD or DATASET_ID_DEV is missing from the environment"
        )
    if default_layer not in VALID_DATASET_LAYERS:
        raise ValueError(
            "FASTAPI_DATASET_LAYER must be one of raw, silver, gold"
        )
    if not credentials_value:
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS is missing from the environment"
        )

    default_limit = int(os.getenv("FASTAPI_DEFAULT_LIMIT", "100"))
    max_limit = int(os.getenv("FASTAPI_MAX_LIMIT", "1000"))
    origins = _parse_origins(os.getenv("FASTAPI_CORS_ORIGINS"))

    return Settings(
        project_id=project_id,
        dataset_base=dataset_id_base,
        dataset_id=dataset_id,
        credentials_path=Path(credentials_value).expanduser(),
        default_limit=default_limit,
        max_limit=max_limit,
        default_layer=default_layer,
        allowed_origins=origins,
    )
