########################################################################################################################

# COMMANDS FOR SETUP DEV ENVIRONMENT

########################################################################################################################

.PHONY: first_init
PYTHON_BIN = $(CURDIR)/.venv/bin/python
FASTAPI_PYTHONPATH = fastapi/src:predict/src
STREAMLIT_APP = dashboard/Accueil_des_dashboards.py
AIRFLOW_RUNTIME_SERVICES = postgres redis airflow-dag-processor airflow-apiserver airflow-scheduler airflow-triggerer airflow-worker

.PHONY: first_init
firts_init :
	pip install poetry
	pip install pre-commit
	pip install codespell
	pre-commit install

.PHONY: setup
setup :
	@echo "Install the module";
	poetry install

########################################################################################################################

# REST API

########################################################################################################################
.PHONY: start_fastapi
start_fastapi:
	PYTHONPATH=$(FASTAPI_PYTHONPATH) $(PYTHON_BIN) -m uvicorn mix_energy_api.main:app --reload --host 0.0.0.0 --port 8890

.PHONY: start_fastapi_dev
start_fastapi_dev:
	PYTHONPATH=$(FASTAPI_PYTHONPATH) $(PYTHON_BIN) -m uvicorn mix_energy_api.main:app --reload --host 0.0.0.0 --port 8890

.PHONY: start_streamlit
start_streamlit:
	cd $(CURDIR)/front-streamlit && FASTAPI_BASE_URL=$${FASTAPI_BASE_URL:-http://localhost:8890} $(PYTHON_BIN) -m streamlit run $(STREAMLIT_APP) --server.port 8501 --server.address 0.0.0.0

########################################################################################################################

# Docker commands

########################################################################################################################


.PHONY: init_local_airflow

AIRFLOW_COMPOSE = docker compose --env-file .env -f airflow/docker-compose.yaml

.PHONY: build_predict
build_predict:
	@echo "Build the predict module";
	cd ${PWD}/predict && poetry build && cd ..;

.PHONY: clean_predict
clean_predict:
	rm -rf ${PWD}/predict/dist

.PHONY: build_local_fastapi
build_local_fastapi: build_predict
	cp ${PWD}/predict/dist/predict-*-py3-none-any.whl fastapi/;
	@echo "Build the docker ${IMAGE}"
	cd ${PWD}/fastapi && docker build -t ${IMAGE} . ;
	cd .. && rm ${PWD}/fastapi/*.whl;

.PHONY: build_local_airflow
build_local_airflow: build_predict
	$(AIRFLOW_COMPOSE) build

.PHONY: build_local_streamlit
build_local_streamlit:
	cd ${PWD}/front-streamlit && docker build -t "mix-energie-streamlit" . && cd .. ;

.PHONY: run_local_mlflow
.PHONY: stop_local_mlflow
.PHONY: start_mlflow_server
start_mlflow_server:
	$(AIRFLOW_COMPOSE) --profile mlflow up -d mlflow

run_local_mlflow: start_mlflow_server

stop_local_mlflow:
	$(AIRFLOW_COMPOSE) stop mlflow

.PHONY: run_local_fastapi
run_local_fastapi:
# Run local image
	@echo "Run the docker image"
	docker run --rm -p ${HOST_PORT}:${PORT} \
			--volume ${PWD}/data:/app/data:ro \
			-e PROJECT_ID=${PROJECT_ID} \
			-e DATASET_ID_PROD=${DATASET_ID_PROD} \
			-e GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} \
			-e MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI} \
			${IMAGE}

.PHONY: init_local_airflow
init_local_airflow:
	@set -e; \
	$(AIRFLOW_COMPOSE) up -d postgres redis >/dev/null; \
	container_id="$$($(AIRFLOW_COMPOSE) --profile bootstrap run -d --no-deps airflow-init)"; \
	echo "airflow-init container: $$container_id"; \
	docker wait "$$container_id" >/dev/null; \
	exit_code="$$(docker inspect "$$container_id" --format='{{.State.ExitCode}}')"; \
	docker logs "$$container_id"; \
	docker rm -f "$$container_id" >/dev/null; \
	exit "$$exit_code"

.PHONY: run_local_airflow
run_local_airflow:
	$(AIRFLOW_COMPOSE) up -d $(AIRFLOW_RUNTIME_SERVICES)

.PHONY: run_local_airflow_full
run_local_airflow_full:
	$(AIRFLOW_COMPOSE) --profile mlflow up -d mlflow $(AIRFLOW_RUNTIME_SERVICES)

.PHONY: stop_local_airflow
stop_local_airflow:
	$(AIRFLOW_COMPOSE) stop $(AIRFLOW_RUNTIME_SERVICES)

.PHONY: run_local_streamlit
run_local_streamlit:
	docker run --rm -p 8501:8501 "mix-energie-streamlit"

.PHONY: coffee
coffee: build_local_streamlit build_local_fastapi build_local_airflow

.PHONY: spring_clean
spring_clean: clean_predict stop_local_airflow
	docker stop $(docker ps -a -q)
	yes | docker system prune -a

# .PHONY: run_cat
# run_cat: run_local_fastapi,run_local_airflow,run_local_streamlit,start_mlflow_server


# .PHONY: build_gcp
# build_gcp:
# # Build the image for GCP (Linux/amd64 platform required for Cloud Run)
# 	docker build --platform linux/amd64 -t ${LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE} --file fastapi/Dockerfile .
#
# .PHONY: push_gcp
# push_gcp: build_gcp
# # Push the image to Artifact Registry
# 	docker push ${LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE}

# .PHONY: auth_gcp
# auth_gcp:
# 	gcloud auth login
# 	gcloud config set project ${PROJECT_ID}

# .PHONY: deploy
# deploy:
# 	gcloud run deploy ${IMAGE} --image ${LOCATION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE} --region ${LOCATION} --platform managed --allow-unauthenticated
