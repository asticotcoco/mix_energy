from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag, task

from mix_energy.airflow_dbt import (
    build_dbt_run_command,
    validate_dbt_target_datasets,
)
from mix_energy.bucket_to_bigquery_airflow import run_transfer as _run_transfer
from mix_energy.meteo_ingest import collect_meteo_csv_contents

FILE_PREFIX = "meteo"
GCP_CONN_ID = "google_cloud_default"
BUCKET_NAME = os.getenv("BUCKET_NAME", "mix-energie-bucket")
DBT_DIR = "/opt/project/dbt"


@dag(
    dag_id="dag_meteo",
    description="Ingestion meteo vers GCS puis BigQuery.",
    start_date=datetime(2026, 1, 1),
    schedule="0 6 * * *",
    catchup=False,
    tags=["meteo", "ingestion"],
)
def dag_meteo():
    @task(task_id="check_bucket_connection")
    def check_bucket_connection() -> str:
        hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        try:
            hook.list(bucket_name=BUCKET_NAME, max_results=1)
        except Exception as exc:
            raise RuntimeError("Connexion au bucket GCP impossible.") from exc
        return BUCKET_NAME

    @task(task_id="ingest_csv_to_bucket")
    def ingest_csv_to_bucket(bucket_name: str) -> None:
        csv_contents = collect_meteo_csv_contents()
        if not csv_contents:
            raise RuntimeError("Recuperation meteo echouee ou aucune donnee disponible.")

        if BUCKET_NAME != bucket_name:
            raise RuntimeError(
                f"Bucket inattendu: '{BUCKET_NAME}' (attendu: '{bucket_name}')."
            )

        hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        uploaded_files = 0

        for object_name, csv_content in csv_contents.items():
            if len(csv_content) == 0:
                raise RuntimeError(f"CSV vide recupere pour {object_name}.")

            hook.upload(
                bucket_name=bucket_name,
                object_name=object_name,
                data=csv_content,
            )
            uploaded_files += 1

        if uploaded_files == 0:
            raise RuntimeError("Aucun fichier meteo n'a ete charge dans le bucket.")

    @task(task_id="transfer_csv_to_bigquery")
    def transfer_csv_from_bucket_to_bigquery() -> None:
        _run_transfer(file_prefix=FILE_PREFIX, gcp_conn_id=GCP_CONN_ID)

    @task(task_id="check_dbt_target_datasets")
    def check_dbt_target_datasets() -> None:
        validate_dbt_target_datasets(["silver"], gcp_conn_id=GCP_CONN_ID)

    check_bucket_connection_task: Any = check_bucket_connection()
    ingest_csv_to_bucket_task: Any = ingest_csv_to_bucket(
        bucket_name=check_bucket_connection_task,
    )
    transfer_csv_from_bucket_to_bigquery_task: Any = (
        transfer_csv_from_bucket_to_bigquery()
    )
    check_dbt_target_datasets_task: Any = check_dbt_target_datasets()

    dbt_meteo = BashOperator(
        task_id="dbt_meteo",
        bash_command=build_dbt_run_command(
            ["meteo_by_city"],
            dbt_dir=DBT_DIR,
        ),
    )

    (
        check_bucket_connection_task
        >> ingest_csv_to_bucket_task
        >> transfer_csv_from_bucket_to_bigquery_task
        >> check_dbt_target_datasets_task
        >> dbt_meteo
    )


dag = dag_meteo()