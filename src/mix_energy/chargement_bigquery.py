import argparse
import importlib
import logging
import os
import re
from dataclasses import dataclass
from typing import Any

from google.api_core.exceptions import NotFound


CSV_DELIMITER_SEMICOLON = ";"
CSV_DELIMITER_COMMA = ","


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Settings:
    project_id: str
    dataset_id: str
    bucket_name: str
    prefix: str = ""

    @classmethod
    def from_env(cls, prefix_override: str | None = None) -> "Settings":
        project_id = os.getenv("PROJECT_ID")
        dataset_id = os.getenv("DATASET_ID") or os.getenv("DATASET_ID_PROD")
        bucket_name = os.getenv("BUCKET_NAME")
        prefix = prefix_override if prefix_override is not None else os.getenv("PREFIX", "")

        missing_vars = [
            name
            for name, value in (
                ("PROJECT_ID", project_id),
                ("DATASET_ID or DATASET_ID_PROD", dataset_id),
                ("BUCKET_NAME", bucket_name),
            )
            if not value
        ]
        if missing_vars:
            raise ValueError(
                "Variables d'environnement manquantes: {}".format(
                    ", ".join(missing_vars)
                )
            )

        return cls(
            project_id=project_id,
            dataset_id=dataset_id,
            bucket_name=bucket_name,
            prefix=prefix,
        )


def build_clients(project_id: str) -> tuple[Any, Any]:
    storage_module = _load_storage_module()
    bigquery_module = _load_bigquery_module()
    return storage_module.Client(project=project_id), bigquery_module.Client(
        project=project_id
    )


def _load_bigquery_module() -> Any:
    return _load_google_cloud_module(
        module_name="google.cloud.bigquery",
        package_name="google-cloud-bigquery",
    )


def _load_storage_module() -> Any:
    return _load_google_cloud_module(
        module_name="google.cloud.storage",
        package_name="google-cloud-storage",
    )


def _load_google_cloud_module(module_name: str, package_name: str) -> Any:
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            f"Le package {package_name} est requis pour executer ce script."
        ) from exc


def normalize_table_name(filename: str) -> str:
    table_name = filename.rsplit("/", maxsplit=1)[-1].removesuffix(".csv")
    normalized = re.sub(r"[^0-9a-zA-Z_]+", "_", table_name).strip("_").lower()

    if not normalized:
        raise ValueError(f"Nom de table invalide derive de {filename}")
    if normalized[0].isdigit():
        normalized = f"t_{normalized}"

    return normalized


def get_csv_delimiter(filename: str) -> str:
    filename_lower = filename.lower()
    if filename_lower.startswith("meteo") or filename_lower.startswith("air_quality"):
        return CSV_DELIMITER_COMMA
    return CSV_DELIMITER_SEMICOLON


def table_exists(bq_client: Any, table_id: str) -> bool:
    try:
        bq_client.get_table(table_id)
        return True
    except NotFound:
        return False


def iter_csv_blob_names(
    storage_client: Any,
    bucket_name: str,
    prefix: str = "",
    file_prefix: str | None = None,
) -> list[str]:
    bucket = storage_client.bucket(bucket_name)
    matched_blobs = []
    normalized_file_prefix = file_prefix.lower() if file_prefix else None

    for blob in bucket.list_blobs(prefix=prefix or None):
        if not blob.name.endswith(".csv"):
            continue

        filename = blob.name.rsplit("/", maxsplit=1)[-1]
        if normalized_file_prefix and not filename.lower().startswith(
            normalized_file_prefix
        ):
            continue

        matched_blobs.append(blob.name)

    return matched_blobs


def load_blob_to_table(
    bq_client: Any,
    settings: Settings,
    blob_name: str,
) -> str:
    bigquery_module = _load_bigquery_module()
    filename = blob_name.rsplit("/", maxsplit=1)[-1]
    table_name = normalize_table_name(filename)
    table_id = f"{settings.project_id}.{settings.dataset_id}.{table_name}"
    uri = f"gs://{settings.bucket_name}/{blob_name}"
    write_disposition = (
        bigquery_module.WriteDisposition.WRITE_APPEND
        if table_exists(bq_client, table_id)
        else bigquery_module.WriteDisposition.WRITE_EMPTY
    )

    job_config = bigquery_module.LoadJobConfig(
        autodetect=True,
        source_format=bigquery_module.SourceFormat.CSV,
        skip_leading_rows=1,
        field_delimiter=get_csv_delimiter(filename),
        write_disposition=write_disposition,
    )

    logger.info("Chargement %s -> %s (%s)", uri, table_id, write_disposition)
    load_job = bq_client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()

    if load_job.errors:
        raise RuntimeError(f"Chargement BigQuery en echec pour {blob_name}: {load_job.errors}")

    table = bq_client.get_table(table_id)
    logger.info("Table %s chargee, %s ligne(s) totales", table_id, table.num_rows)
    return table_id


def run_transfer(
    file_prefix: str | None = None,
    prefix_override: str | None = None,
    storage_client: Any | None = None,
    bq_client: Any | None = None,
) -> list[str]:
    settings = Settings.from_env(prefix_override=prefix_override)

    if storage_client is None or bq_client is None:
        storage_client, bq_client = build_clients(settings.project_id)

    blob_names = iter_csv_blob_names(
        storage_client=storage_client,
        bucket_name=settings.bucket_name,
        prefix=settings.prefix,
        file_prefix=file_prefix,
    )
    if not blob_names:
        logger.warning(
            "Aucun fichier CSV trouve dans gs://%s/%s",
            settings.bucket_name,
            settings.prefix,
        )
        return []

    loaded_tables = []
    for blob_name in blob_names:
        loaded_tables.append(load_blob_to_table(bq_client, settings, blob_name))

    return loaded_tables


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Charge des fichiers CSV depuis GCS vers BigQuery."
    )
    parser.add_argument(
        "file_prefix",
        nargs="?",
        default=None,
        help="Prefixe optionnel du nom de fichier a charger, par exemple eco2mix-national-cons.",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Prefixe GCS optionnel pour restreindre la recherche des blobs.",
    )
    args = parser.parse_args()

    loaded_tables = run_transfer(
        file_prefix=args.file_prefix,
        prefix_override=args.prefix,
    )
    logger.info("Transfert termine: %s table(s) traitee(s)", len(loaded_tables))


if __name__ == "__main__":
    main()
