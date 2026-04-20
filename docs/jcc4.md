# Script oral de soutenance 20 minutes

## Candidat

- Nom : Charbonnel
- Prenom : Jean-Christophe
- Centre de formation : Artefact
- Projet : Mix Energy
- Bloc : RNCP37827BC01

## Positionnement du document

Ce script est construit en se basant sur deux sources.

La premiere est le code reel du projet Mix Energy, afin que chaque affirmation puisse etre defendue devant le jury a partir d'elements concrets du depot.

La seconde est le document dossier_RNCP37827BC01_Merville_Thibault_Mix-Energie.pdf, dont je reprends la logique de decoupage : resume du projet, collecte automatisee, preparation des donnees, base de donnees, API, deploiement, infrastructure et conclusion.

L'objectif est donc de produire une soutenance orale de 20 minutes qui soit plus proche d'un dossier technique structure que d'un simple pitch. Ce document n'est pas fait pour etre lu mot a mot. Il sert de fil conducteur, avec des blocs de code a afficher aux moments importants.

## Decoupage cible pour 20 minutes

- 1. Resume du projet et architecture du pipeline : 2 min
- 2. Collecter les donnees de maniere automatisee : 4 min
- 3. Preparation, nettoyage et aggregation : 4 min 30
- 4. Base de donnees et tracabilite : 2 min
- 5. Mise a disposition via API et dashboard : 3 min
- 6. Deploiements : 1 min
- 7. Infrastructure as Code avec Terraform : 1 min 30
- 8. Conclusion et axes d'amelioration : 2 min

## Conseils d'usage

Quand un bloc de code apparait, il faut commenter son role, le risque qu'il traite, et la valeur qu'il apporte. Il ne faut pas lire le code ligne par ligne. Le bon rythme est un debit calme avec une transition claire entre chaque section.

---

## 1. Resume du projet et architecture du pipeline - 2 min

Bonjour, je vais vous presenter le projet Mix Energy, que nous avons developpe dans le cadre du bloc RNCP37827BC01, autour de la collecte, du stockage et de la mise a disposition des donnees d'un projet d'intelligence artificielle.

Le projet Mix Energy est un pipeline de donnees centre sur le mix electrique francais. Son objectif est de recuperer des donnees de production et de consommation electriques, de les historiser, de les transformer en indicateurs metier exploitables, de calculer une intensite carbone, puis de mettre ces donnees a disposition via une API et un dashboard. Une brique predictive vient completer cet ensemble afin d'estimer la consommation a court terme.

Ce qui fait la valeur du projet, ce n'est pas un composant isole, mais la coherence de la chaine complete. Nous avons une couche de collecte automatisee, une couche de stockage brut, une couche de transformation analytique, une couche d'exposition via API, une couche de restitution avec Streamlit, et enfin une couche d'industrialisation avec Docker, Airflow, MLflow et Terraform.

Ce decoupage est important a expliquer au jury, parce qu'il montre que nous avons travaille comme des data engineers et pas seulement comme des analysts. Nous n'avons pas cherche a produire uniquement un tableau de bord. Nous avons construit un pipeline exploitable, evolutif et relativement industrialisable.

Si je devais resumer l'architecture en une phrase, je dirais que Mix Energy transforme des donnees ouvertes heterogenes en un service analytique reutilisable, capable a la fois de restituer l'etat du systeme electrique francais et de preparer un usage predictif.

---

## 2. Collecter les donnees de maniere automatisee - 4 min

La premiere etape du pipeline consiste a ingerer plusieurs jeux de donnees ouverts. Le coeur du projet repose sur les datasets Eco2mix, nationaux et regionaux, en temps reel et en consolide. Le projet integre egalement la base carbone, et le depot contient deja des briques pour la meteo et la qualite de l'air, meme si ces enrichissements ne sont pas encore au meme niveau de valorisation dans le front.

L'idee importante a faire passer est la suivante : la collecte ne se limite pas a appeler une URL. Nous avons cherche a rendre cette collecte fiable, traçable et compatible avec une orchestration recurrente.

### Bloc de code 1 - Recuperation d'un CSV Eco2mix

Source : ingest_dbt/src/mix_energy/eco2mix_ingest.py

```python
def retrieve_csv(
    dataset_id: str,
    delimiter: str = ";",
    list_sep: str = ",",
    quote_all: bool = False,
    with_bom: bool = True,
):
    req_url = base_url + dataset_id + "/exports/csv"

    params = {
        "delimiter": delimiter,
        "list_separator": list_sep,
        "quote_all": quote_all,
        "with_bom": with_bom,
    }

    result = __perform_request(req_url=req_url, params=params)

    if result.status_code == 200:
        if (
            "content-type" in result.headers
            and result.headers["content-type"].split(";")[0] == "text/csv"
        ):
            logger.info("CSV file of the dataset {} retrieved", dataset_id)
            return result.content
    else:
        return None
```

Quand je presente ce premier bloc, j'explique que la logique de collecte est volontairement simple a l'interface, mais defensive dans son execution. La fonction recupere directement le CSV d'un dataset via l'endpoint d'export. Elle ne passe pas par un fichier intermediaire local et renvoie les bytes du CSV, ce qui facilite l'enchainement avec l'etape de depot dans le bucket.

Le point le plus important n'est pas seulement le GET HTTP, c'est le controle du content-type et la gestion des retours d'erreur, qui sont traites dans __perform_request. Cela evite de stocker par erreur un payload inattendu ou une erreur JSON a la place du fichier attendu.

### Bloc de code 2 - Connexion au bucket et upload GCS

Source : ingest_dbt/src/mix_energy/gcp_utils.py

```python
def connect_to_bucket() -> storage.Bucket:
    json_credential_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("PROJECT_ID")

    if not json_credential_file:
        json_credential_file = os.path.join(
            os.path.dirname(__file__), "data/meteo/mix-energie-gcp-23501901f9c9.json"
        )
    if not os.path.exists(json_credential_file):
        get_logger().error(
            f"Fichier de credentials introuvable : {json_credential_file}"
        )
        return None

    credentials = service_account.Credentials.from_service_account_file(
        json_credential_file
    )
    client = storage.Client(project=project_id, credentials=credentials)
    bucket = client.get_bucket("mix-energie-bucket")
    return bucket

def upload_data_in_bucket(bucket, data, dataset):
    blob = bucket.blob(dataset + ".csv")
    blob.upload_from_string(data)
```

Ce second bloc permet de montrer la jonction entre la collecte et le stockage brut. Les donnees ne restent pas dans la memoire du script ou dans un dossier local fragile. Elles sont envoyees dans Google Cloud Storage, qui joue le role de zone brute. Cette etape est importante car elle separe clairement l'extraction de la transformation. On archive d'abord, on nettoie ensuite.

### Bloc de code 3 - Orchestration Airflow

Source : airflow/dags/dag_eco2mix_national_tr.py

```python
@dag(
    dag_id="dag_eco2mix_national_tr",
    description="Ingestion eco2mix national tr vers GCS.",
    start_date=datetime(2026, 1, 1),
    schedule=MultipleCronTriggerTimetable(
        "30,45 9 * * 1-5",
        "0,15,30,45 10-17 * * 1-5",
        "0,15,30 18 * * 1-5",
        timezone="Europe/Paris",
    ),
    catchup=False,
    tags=["eco2mix", "ingestion"],
)
def dag_eco2mix_national_tr():
    ...
    (
        check_bucket_connection_task
        >> ingest_csv_to_bucket_task
        >> transfer_csv_from_bucket_to_bigquery_task
        >> check_dbt_target_datasets_task
        >> dbt_eco2mix_national_tr
    )
```

Ce DAG est un bon exemple pour expliquer l'orchestration. Nous avons ici une planification multi-plages adaptee aux mises a jour en journee, un controle de connectivite au bucket, une ingestion, un transfert vers BigQuery, puis le declenchement de dbt. Cela montre que le pipeline est pense comme une chaine ordonnee, et non comme un enchainement manuel de scripts.

Devant le jury, j'insiste sur le fait qu'Airflow apporte trois choses : la planification, la lisibilite des dependances, et l'observabilite en cas d'echec.

---

## 3. Preparation, nettoyage et aggregation - 4 min 30

Le dossier de Thibault insistait sur un point important : le pipeline n'est pas strictement ELT au sens idealise du terme, car une partie du pre-nettoyage doit etre faite avant chargement, notamment pour fiabiliser les schemas BigQuery. Cette observation reste pertinente dans le code actuel. En pratique, nous sommes plus proches d'un ETLT : extraction, pre-traitement cible, chargement, puis transformation analytique plus riche avec dbt.

### Bloc de code 4 - Inference dynamique des schemas BigQuery

Source : ingest_dbt/src/mix_energy/bigquery_schema_generator.py

```python
def create_bigquery_schema_for_file(
    filename: str, df: pd.DataFrame
) -> list[bigquery.SchemaField]:
    filename_lower = filename.lower()

    if filename_lower.startswith("eco2mix"):
        return create_eco2mix_schema(df)
    if filename_lower.startswith("meteo"):
        return create_meteo_schema(df)
    if filename_lower.startswith("air_quality"):
        return create_air_quality_schema(df)
    return create_generic_schema(df)
```

Ce bloc est tres utile a montrer parce qu'il demontre un point d'ingenierie souvent invisible : nous n'avons pas hard-code a la main un schema unique pour tous les fichiers. Le projet choisit une logique de schema par famille de sources. Cela rend l'ingestion plus souple et permet de preparer l'arrivee de nouvelles sources comme la meteo ou la qualite de l'air.

### Bloc de code 5 - Regles de typage pour Eco2mix

Source : ingest_dbt/src/mix_energy/bigquery_schema_generator.py

```python
def _resolve_eco2mix_type(column_name: Any, dtype: Any) -> str:
    col_str = str(column_name).lower()

    if "time" in col_str or "timestamp" in col_str or "date_heure" in col_str:
        return "TIMESTAMP"
    if "date" in col_str and "heure" not in col_str:
        return "DATE"
    if "heure" in col_str:
        return "STRING"
    if "libelle_region" in col_str or "nature" in col_str or "perimetre" in col_str:
        return "STRING"
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    if pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    return "STRING"
```

Quand je commente ce bloc, j'explique que le nettoyage ne commence pas dans dbt, mais des la comprehension du fichier source. Ici, les dates, timestamps, identifiants textuels et mesures numeriques sont resolus selon des regles metier simples mais robustes. Cela evite d'introduire trop tot des ambiguities de typage dans BigQuery.

### Bloc de code 6 - Silver incremental avec dbt

Source : dbt/models/silver/eco2mix_national_cons_def_histo.sql

```sql
{{ config(
    alias='eco2mix_national_cons_def_histo',
    materialized='incremental',
    unique_key='date'
) }}

SELECT
perimetre       AS perimetre,
nature          AS nature,
date            AS date,
heure           AS heure,
date_heure      AS date_heure,
consommation    AS consommation,
prevision_j1    AS prevision_j1,
prevision_j     AS prevision_j,
taux_co2        AS taux_co2
FROM {{source('nat_source','eco2mix_national_cons_def')}}

{% if is_incremental() %}
    WHERE date > (SELECT MAX(date) FROM {{ this }})
{% endif %}
```

Cette couche silver sert a historiser proprement les donnees consolidees nationales. Devant le jury, je peux expliquer que le choix incremental est important pour deux raisons : il evite les duplications et il limite les couts de requetes en ne retraitant que les dates nouvelles.

### Bloc de code 7 - Aggregation journaliere et taux CO2 pondere

Source : dbt/models/gold/nat_cons_agre_j.sql

```sql
select
DATE(date) as date,
sum((consommation - pompage  - ech_physiques)) *0.5 as production,
sum(consommation) * 0.5 as consommation,
sum(prevision_j1) * 0.25 as prevision_j1,
sum(prevision_j) * 0.25 as prevision_j,
sum(taux_co2  * (consommation - pompage  - ech_physiques)) /
NULLIF(sum((consommation - pompage  - ech_physiques)), 0) AS taux_co2
from {{ ref('eco2mix_national_cons_def_histo') }}
{% if is_incremental() %}
    WHERE date > (SELECT MAX(date) FROM {{ this }})
{% endif %}
group by perimetre, nature, date, annee, mois, jour
order by date asc
```

Ce bloc montre la transformation metier la plus interessante du projet. Les donnees demi-horaires sont converties en grandeurs journalieres, et le taux de CO2 est calcule comme une moyenne ponderee par la production nette. C'est ici que la donnee brute devient un indicateur interpretable.

### Bloc de code 8 - Preparation pour la prediction et pipeline ML

Sources : dbt/models/gold/nat_tr_predi.sql et predict/src/predict/preproc.py

```sql
SELECT
consommation,
prevision_j1,
prevision_j,
EXTRACT(YEAR FROM date_heure) AS year,
EXTRACT(MONTH FROM date_heure) AS month,
EXTRACT(DAY FROM date_heure) AS day,
EXTRACT(HOUR FROM date_heure) AS hour,
EXTRACT(MINUTE FROM date_heure) AS minute
FROM {{ source('nat_source', 'eco2mix_national_tr') }}
WHERE EXTRACT(YEAR FROM date_heure) = EXTRACT(YEAR FROM CURRENT_DATE())
and consommation is not null
```

```python
def build_pipeline() -> Pipeline:
    num_pipe = Pipeline(
        [("knn_imp", KNNImputer(n_neighbors=5)), ("scaler", StandardScaler())]
    )

    preprocessor = ColumnTransformer(
        [("numeric", num_pipe, make_column_selector(dtype_include="number"))]
    ).set_output(transform="pandas")

    return preprocessor
```

Ici, je peux montrer le lien entre data engineering et machine learning. dbt prepare des features temporelles propres, puis le module predict applique une pipeline de pretraitement avec imputation KNN et standardisation. Le message important a porter est que la prediction n'est pas hors-sol : elle repose sur les tables gold et sur un flux reproductible.

---

## 4. Base de donnees et tracabilite - 2 min

Le choix de BigQuery comme entrepot principal est logique pour ce projet. Nous sommes sur des donnees tabulaires, analytiques, avec une volumetrie raisonnable mais evolutive, et avec un besoin fort de requetage SQL et d'integration native a GCP.

### Bloc de code 9 - Chargement de CSV vers BigQuery

Source : ingest_dbt/src/mix_energy/bigquery_loader.py

```python
def load_csv_to_bigquery(
    bq_client: bigquery.Client,
    uri: str,
    table_id: str,
    schema: list[bigquery.SchemaField] | None = None,
    write_disposition: str = bigquery.WriteDisposition.WRITE_TRUNCATE,
    field_delimiter: str = CSV_DELIMITER_SEMICOLON,
) -> bool:
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=schema,
        autodetect=schema is None,
        write_disposition=write_disposition,
        field_delimiter=field_delimiter,
        null_markers=NULL_MARKERS,
    )

    load_job = bq_client.load_table_from_uri(uri, table_id, job_config=job_config)
```

Ce bloc me permet d'expliquer que la base de donnees n'est pas uniquement une destination finale. Elle fait partie d'une chaine de chargement maitrisee, avec delimiter, gestion des nulls, schema explicite ou autodetect. C'est important pour la fiabilite.

### Bloc de code 10 - Table de suivi des fichiers charges

Source : ingest_dbt/src/mix_energy/bigquery_loader.py

```python
def mark_file_as_loaded(client: bigquery.Client, filename: str):
    table_id = f"{PROJECT_ID}.{DATASET_ID}._loaded_files"
    rows = [
        {
            "filename": filename,
            "loaded_at": datetime.now(timezone.utc).isoformat(),
        }
    ]

    schema = [
        bigquery.SchemaField("filename", "STRING"),
        bigquery.SchemaField("loaded_at", "TIMESTAMP"),
    ]
    table = bigquery.Table(table_id, schema=schema)
    client.create_table(table, exists_ok=True)
    client.insert_rows_json(table_id, rows)
```

Ce point est tres interessant a valoriser : le projet garde une trace des fichiers charges. Cela apporte une forme d'auditabilite et montre que nous avons pense a la traçabilite des runs. J'ajoute aussi oralement que le risque RGPD est tres faible ici, car nous manipulons des donnees publiques, techniques et non personnelles.

---

## 5. Mise a disposition via API et dashboard - 3 min

Une fois les donnees transforme es, il faut les rendre consultables proprement. Nous avons choisi FastAPI pour exposer les datasets sous forme de service REST en lecture seule. Ce choix permet d'isoler BigQuery, de mieux controler les requetes et de donner au front un point d'entree stable.

### Bloc de code 11 - Schémas Pydantic et validation stricte

Source : fastapi/src/mix_energy_api/schemas.py

```python
FilterOperator = Literal[
    "eq",
    "ne",
    "lt",
    "lte",
    "gt",
    "gte",
    "contains",
    "in",
    "is_null",
    "not_null",
]

class FilterClause(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(..., min_length=1)
    operator: FilterOperator
    value: Any | list[Any] | None = None
```

Ce bloc est important car il montre que l'API ne prend pas des filtres libres sans controle. Les operateurs sont bornes, les champs supplementaires interdits, et les payloads sont valides. Cela apporte de la robustesse et limite les usages non prevus.

### Bloc de code 12 - Endpoint generique de requete

Source : fastapi/src/mix_energy_api/main.py

```python
@app.get("/tables/{table_name}", response_model=QueryResponse)
def query_table(
    request: Request,
    table_name: str,
    columns: str | None = Query(default=None),
    filters: str | None = Query(default=None),
    layer: DatasetLayer = Query(default="gold"),
    limit: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    service = get_service(request, layer=layer)
    parsed_columns = _parse_columns(columns)
    parsed_filters = _parse_filters(filters)
    return service.query_table(
        table_name,
        columns=parsed_columns,
        filters=parsed_filters,
        limit=limit,
    )
```

Je peux expliquer ici que l'API est volontairement generique, ce qui la rend reutilisable pour plusieurs tables et plusieurs couches. Cela evite de dupliquer une route par table. En meme temps, elle reste encadree par les schemas et la couche de service BigQuery.

### Bloc de code 13 - CORS et consommation depuis le front

Sources : fastapi/src/mix_energy_api/main.py et front-streamlit/dashboard/data_api_client.py

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)
```

```python
def query_table(
    self,
    table_name: str,
    *,
    filters: list[dict[str, Any]] | None = None,
    limit: int | None = None,
    layer: str = DEFAULT_LAYER,
) -> dict[str, Any]:
    params = {"limit": limit or self.per_call_limit, "layer": layer}
    if filters:
        params["filters"] = json.dumps(filters, ensure_ascii=False)
    return self._safe_get_json(f"/tables/{table_name}", params=params)
```

Ce double extrait montre bien l'architecture cible : FastAPI gere les acces autorises, et Streamlit consomme l'API via un client dedie. Devant le jury, j'explique que cela permet de decoupler proprement la presentation des donnees de leur stockage.

---

## 6. Deploiements - 1 min

Le projet est conteneurise avec plusieurs Dockerfiles et un docker-compose pour Airflow. Cet aspect est important car il permet d'avoir un environnement de developpement et de demonstration plus reproductible.

### Bloc de code 14 - Volumes et services dans Airflow

Source : airflow/docker-compose.yaml

```yaml
volumes:
  - ${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags
  - ${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs
  - ${AIRFLOW_PROJ_DIR:-.}/config:/opt/airflow/config
  - ${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins
  - ../dbt/profiles.yml.exemple:/home/airflow/.dbt/profiles.yml:ro
  - ../ingest_dbt/src:/opt/project/src:ro
  - ../dbt:/opt/project/dbt
  - ../data/gcp:/opt/project/data/gcp:ro
```

Ce bloc montre que l'environnement Airflow embarque les DAGs, les logs, le code d'ingestion, la configuration dbt et les credentials montes en lecture seule. C'est une bonne illustration de l'integration technique du projet.

Le Makefile simplifie ensuite les operations de build et de lancement pour FastAPI, Airflow, Streamlit et MLflow. C'est un detail pratique, mais utile a mettre en avant car il montre une attention portee a l'exploitabilite du projet.

---

## 7. Infrastructure as Code avec Terraform - 1 min 30

L'infrastructure cloud est decrite avec Terraform. C'est une brique importante dans une soutenance de data engineering parce qu'elle montre que le projet ne depend pas uniquement de manipulations manuelles dans la console GCP.

### Bloc de code 15 - Provisioning GCP declaratif

Source : iac/main.tf

```hcl
resource "google_project" "mix_energie_gcp" {
  name                = var.TF_VAR_project_name
  project_id          = var.TF_VAR_project_id
  org_id              = var.TF_VAR_org_id
  billing_account     = var.TF_VAR_billing_account
  auto_create_network = true
}

resource "google_project_service" "bigquery" {
  project            = google_project.mix_energie_gcp.project_id
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

resource "google_storage_bucket" "mix_energie_bucket" {
  name                        = local.project_bucket_name
  location                    = local.bucket_location
  project                     = google_project.mix_energie_gcp.project_id
  uniform_bucket_level_access = true
}
```

Ce que je souligne ici, c'est la reproductibilite. Le projet GCP, les APIs, le bucket et les autres ressources sont declares comme du code. Cela permet de reconstruire l'environnement, de le versionner et de limiter les erreurs humaines. C'est aussi un point fort pour la collaboration en equipe.

---

## 8. Conclusion et axes d'amelioration - 2 min

Pour conclure, Mix Energy est un projet de pipeline data complet. Il part de sources ouvertes, les collecte de maniere automatisee, les stocke dans une zone brute, les charge dans BigQuery, les transforme avec dbt, les expose via FastAPI, les restitue dans Streamlit, et prepare une premiere brique de prediction avec versioning MLflow.

La vraie force du projet est sa coherence. Chaque composant est relie au suivant. Les choix techniques sont lisibles : Airflow pour orchestrer, GCS pour le brut, BigQuery pour l'analytique, dbt pour la transformation, FastAPI pour l'exposition, Streamlit pour la restitution, Terraform pour l'infrastructure.

Je terminerai en mentionnant plusieurs axes d'amelioration, qui sont d'ailleurs coherents avec ceux du dossier de Thibault et avec l'etat du depot actuel.

- Mieux exploiter les donnees meteo pour enrichir les predictions.
- Valoriser davantage les donnees de qualite de l'air dans les tables gold et dans le dashboard.
- Historiser plus finement les ecarts entre donnees temps reel et donnees consolidees.
- Renforcer les controles de qualite de donnees et l'observabilite.
- Pousser le projet vers un deploiement plus accessible en dehors d'une seule VM.

Ma conclusion orale est donc la suivante : Mix Energy n'est pas simplement une visualisation du mix electrique. C'est une chaine data defendable de bout en bout, qui montre la capacite a collecter, stocker, transformer et exposer des donnees de maniere industrialisable.

Je vous remercie pour votre attention, et je suis disponible pour vos questions.

---

## Questions probables du jury

### Pourquoi avoir choisi BigQuery ?

Parce qu'il s'integre naturellement a GCP, qu'il est adapte aux usages analytiques SQL, et qu'il permet de separer clairement tables brutes, silver et gold.

### Pourquoi avoir ajoute une API au lieu de connecter Streamlit directement a BigQuery ?

Parce que l'API joue le role de couche d'abstraction, de validation et de securisation. Elle permet aussi de reutiliser les donnees dans d'autres consommateurs qu'un seul front.

### Pourquoi parler d'ETLT plutot que d'ELT ?

Parce qu'une partie du nettoyage et de la gestion des schemas doit etre faite avant chargement dans BigQuery, puis les transformations analytiques sont faites ensuite avec dbt.

### Pourquoi le modele de prediction reste-t-il simple ?

Parce que l'objectif etait d'abord de mettre en place une baseline explicable et integree dans un pipeline complet, avec pretraitement, versioning et exposition des predictions.

### Quelle est la prochaine etape la plus utile ?

L'enrichissement par les donnees meteo, car il a un impact direct sur la qualite des predictions et sur la valeur metier du projet.