from __future__ import annotations

import os
from collections.abc import Sequence

from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook


DEFAULT_DBT_DIR = "/opt/project/dbt"
VALID_DBT_TARGETS = {"dev", "prod"}


def get_dbt_target() -> str:
    target = os.getenv("DBT_TARGET", "prod").strip().lower()
    if target not in VALID_DBT_TARGETS:
        valid_targets = ", ".join(sorted(VALID_DBT_TARGETS))
        raise RuntimeError(
            f"DBT_TARGET='{target}' invalide. Valeurs attendues: {valid_targets}."
        )
    return target


def get_project_id() -> str:
    project_id = os.getenv("PROJECT_ID", "").strip()
    if not project_id:
        raise RuntimeError("PROJECT_ID manquant dans l'environnement.")
    return project_id


def get_bigquery_location() -> str:
    location = (
        os.getenv("BIGQUERY_LOCATION", "").strip()
        or os.getenv("TF_VAR_location", "").strip()
        or os.getenv("LOCATION", "").strip()
    )
    if not location:
        raise RuntimeError(
            "BIGQUERY_LOCATION/TF_VAR_location/LOCATION manquant dans l'environnement."
        )
    return location


def get_dbt_dataset_base(target: str | None = None) -> str:
    effective_target = target or get_dbt_target()
    env_name = "DATASET_ID_PROD" if effective_target == "prod" else "DATASET_ID_DEV"
    dataset_base = os.getenv(env_name, "").strip()
    if not dataset_base:
        raise RuntimeError(f"{env_name} manquant dans l'environnement.")
    return dataset_base


def get_required_dbt_dataset_ids(suffixes: Sequence[str]) -> list[str]:
    dataset_base = get_dbt_dataset_base()
    dataset_ids: list[str] = []

    for suffix in suffixes:
        cleaned_suffix = suffix.strip().strip("_")
        dataset_ids.append(
            f"{dataset_base}_{cleaned_suffix}" if cleaned_suffix else dataset_base
        )

    return dataset_ids


def build_dbt_run_command(
    selections: Sequence[str], dbt_dir: str = DEFAULT_DBT_DIR
) -> str:
    if not selections:
        raise RuntimeError("Aucune selection dbt fournie.")

    target = get_dbt_target()
    commands = [f"cd {dbt_dir}"]
    commands.extend(f"dbt run --select {selection} --target {target}" for selection in selections)
    return " &&\n        ".join(commands)


def validate_dbt_target_datasets(
    suffixes: Sequence[str], gcp_conn_id: str = "google_cloud_default"
) -> None:
    project_id = get_project_id()
    expected_location = get_bigquery_location().lower()
    bq_hook = BigQueryHook(gcp_conn_id=gcp_conn_id, use_legacy_sql=False)
    bq_client = bq_hook.get_client(project_id=project_id)

    missing_datasets: list[str] = []
    wrong_location_datasets: list[str] = []

    for dataset_id in get_required_dbt_dataset_ids(suffixes):
        try:
            dataset = bq_client.get_dataset(f"{project_id}.{dataset_id}")
        except Exception:
            missing_datasets.append(dataset_id)
            continue

        dataset_location = (dataset.location or "").lower()
        if dataset_location != expected_location:
            wrong_location_datasets.append(
                f"{project_id}.{dataset_id} (attendu: {expected_location}, actuel: {dataset_location or 'inconnu'})"
            )

    if missing_datasets or wrong_location_datasets:
        details: list[str] = []
        if missing_datasets:
            details.append(
                "datasets manquants: "
                + ", ".join(f"{project_id}.{dataset_id}" for dataset_id in missing_datasets)
            )
        if wrong_location_datasets:
            details.append("datasets avec mauvaise location: " + ", ".join(wrong_location_datasets))

        raise RuntimeError(
            "Validation BigQuery/dbt echouee pour la target "
            f"'{get_dbt_target()}': {' ; '.join(details)}. "
            "Reconcilez l'infrastructure avec iac/deploy_gcp_project.sh "
            "ou corrigez .env et iac/auto.tfvars."
        )