Airflow install

Prerequisites
- Docker and Docker Compose installed.
- Copy the shared environment template:
	cp .env.copy .env

Configure your local user IDs in .env (Linux)
- AIRFLOW_UID must match your host user ID.
- Commands to get them:
	id -u

Start Airflow
- Build/start initialization:
	docker compose --env-file .env -f airflow/docker-compose.yaml --profile bootstrap run --rm airflow-init
- Start only Airflow runtime:
	docker compose --env-file .env -f airflow/docker-compose.yaml up -d postgres redis airflow-dag-processor airflow-apiserver airflow-scheduler airflow-triggerer airflow-worker
- Start MLflow independently:
	docker compose --env-file .env -f airflow/docker-compose.yaml --profile mlflow up -d mlflow
- Start the full local stack explicitly:
	docker compose --env-file .env -f airflow/docker-compose.yaml --profile mlflow up -d mlflow postgres redis airflow-dag-processor airflow-apiserver airflow-scheduler airflow-triggerer airflow-worker

Notes
- This UID setup prevents permission issues on mounted folders (airflow/dags, airflow/logs, airflow/config, airflow/plugins).
- Airflow API/UI is exposed on localhost:8502.
- MLflow UI is exposed on localhost:8503.
- A terminal can appear as "waiting for input" while Docker Compose is still following healthchecks; this startup path is non-interactive.
