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

Source : airflow/dags/dag_air_quality.py

```python
@dag(
    dag_id="dag_air_quality",
    description="Ingestion air quality vers GCS puis BigQuery.",
    start_date=datetime(2026, 1, 1),
    schedule="15 6 * * *",
    catchup=False,
    tags=["air-quality", "ingestion"],
)
def dag_air_quality():
    ...

    (
        check_bucket_connection_task
        >> ingest_csv_to_bucket_task
        >> transfer_csv_from_bucket_to_bigquery_task
        >> check_dbt_target_datasets_task
        >> dbt_air_quality
    )
```

Ce DAG est un bon exemple pour expliquer l'orchestration sur une source d'enrichissement environnementale. Ici, on verifie d'abord l'acces au bucket, on collecte ensuite plusieurs fichiers de qualite de l'air, on les charge vers BigQuery, puis on declenche la transformation dbt de la table silver correspondante. Cela montre que le projet sait orchestrer autre chose que les seuls jeux Eco2mix.

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

### Bloc de code 5 bis - Fonctions de nettoyage des valeurs nulles et des formats

Sources : ingest_dbt/src/mix_energy/bigquery_schema_generator.py et dbt/macros/safe_float64_from_raw.sql

```python
NULL_MARKERS = ["", "NA", "N/A", "null", "NULL", "-", "ND"]

def read_csv_from_gcs(
    gcs_client: storage.Client,
    bucket_name: str,
    blob_name: str,
    sample_rows: int,
    delimiter: str,
) -> pd.DataFrame:
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    with blob.open("rt", encoding="utf-8") as csv_stream:
        df = pd.read_csv(
            cast(Any, csv_stream),
            sep=delimiter,
            dtype=str,
            keep_default_na=True,
            na_values=NULL_MARKERS,
            nrows=sample_rows,
        )

    for col in df.columns:
        col_lower = str(col).lower()
        if "date" in col_lower or "time" in col_lower:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        else:
            if df[col].notna().sum() > 0:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
```

```sql
{% macro safe_float64_from_raw(column_name) -%}
case
    when {{ column_name }} is null then null
    when upper(trim(cast({{ column_name }} as string))) in ('', 'NA', 'N/A', 'NULL', '-', 'ND') then null
    else safe_cast(
        replace(
            regexp_replace(trim(cast({{ column_name }} as string)), r'\s+', ''),
            ',',
            '.'
        ) as float64
    )
end
{%- endmacro %}
```

Fonctions de nettoyage a expliciter a l'oral : le projet traite d'abord les valeurs nulles et les formats incoherents avant meme de raisonner en agregats. Cote ingestion Python, on declare une liste explicite de marqueurs de vide, avec les valeurs "", "NA", "N/A", "null", "NULL", "-" et "ND". Lors de la lecture des CSV, ces marqueurs sont convertis en valeurs manquantes avec na_values, puis les colonnes contenant date ou time sont converties avec pd.to_datetime(errors="coerce"), tandis que les autres colonnes numeriques passent par pd.to_numeric(errors="coerce"). Le choix de errors="coerce" est important : une valeur mal formatee n'arrete pas le pipeline, elle devient null et pourra etre traitee proprement en aval.

On retrouve la meme logique dans dbt pour les colonnes numeriques issues des sources brutes. La macro safe_float64_from_raw convertit d'abord les valeurs vides ou textuelles parasites en null, supprime les espaces, remplace les virgules decimales par des points, puis applique un safe_cast vers FLOAT64. Cela permet de gerer des sources heterogenes sans provoquer d'erreur SQL bloquante. Dans les modeles air quality, on applique aussi des SAFE_CAST explicites sur les dates, timestamps et coordonnees, puis on filtre les lignes dont les champs structurants restent invalides, par exemple avec WHERE SAFE_CAST(date_maj AS TIMESTAMP) IS NOT NULL.

Si le jury me demande un resume simple, je peux dire : nous avons industrialise trois niveaux de nettoyage. Premier niveau, reconnaissance des nulls metier. Deuxieme niveau, normalisation des formats date et numeriques. Troisieme niveau, cast securise en SQL pour empecher qu'une valeur sale fasse echouer tout le pipeline.

### Bloc de code 6 - Silver incremental avec dbt

Source : dbt/models/silver/air_quality_by_city.sql

```sql
{{ config(
    alias='air_quality_by_city',
    materialized='table'
) }}

WITH unioned AS (
    {{ union_city_sources('air_quality_source', 'air_quality_') }}
)

SELECT
    city_name,
    SAFE_CAST(date_maj AS TIMESTAMP) AS date_maj,
    SAFE_CAST(date_dif AS DATE) AS date_dif,
    SAFE_CAST(date_ech AS DATE) AS date_ech,
    SAFE_CAST(x_reg AS FLOAT64) AS x_reg,
    SAFE_CAST(x_wgs84 AS FLOAT64) AS x_wgs84,
    SAFE_CAST(y_reg AS FLOAT64) AS y_reg,
    SAFE_CAST(y_wgs84 AS FLOAT64) AS y_wgs84,
    * EXCEPT(city_name, date_maj, date_dif, date_ech, x_reg, x_wgs84, y_reg, y_wgs84)
FROM unioned
WHERE SAFE_CAST(date_maj AS TIMESTAMP) IS NOT NULL
```

Dans cette variante, la couche silver ne porte plus sur l'historisation d'Eco2mix consolide, mais sur l'unification de plusieurs sources de qualite de l'air au niveau ville. La macro union_city_sources permet de rassembler les fichiers par ville, puis le modele normalise les dates et les coordonnees. Devant le jury, cela permet de montrer que dbt sert aussi a homogeniser des donnees environnementales heterogenes.

### Bloc de code 6 bis - Regles d'agregation pour combiner les sources

Sources : dbt/macros/city_sources.sql et dbt/models/gold/gold_air_quality_by_city.sql

```sql
{% macro union_city_sources(source_name, table_prefix) %}
    {% set cities = get_supported_city_names() %}

    {% for city in cities %}
        SELECT
            '{{ city }}' AS city_name,
            *
        FROM {{ source(source_name, table_prefix ~ city) }}
        {% if not loop.last %}
            UNION ALL
        {% endif %}
    {% endfor %}
{% endmacro %}
```

```sql
WITH ranked_zone_snapshots AS (
        SELECT
                city_name,
                DATE(date_dif) AS date,
                code_zone,
                lib_zone,
                type_zone,
                date_maj,
                SAFE_CAST(code_qual AS INT64) AS code_qual,
                ROW_NUMBER() OVER (
                        PARTITION BY city_name, DATE(date_dif), code_zone
                        ORDER BY date_maj DESC, lib_zone ASC
                ) AS snapshot_rank
        FROM {{ ref('air_quality_by_city') }}
        WHERE date_dif IS NOT NULL
),
latest_zone_snapshots AS (
        SELECT * EXCEPT(snapshot_rank)
        FROM ranked_zone_snapshots
        WHERE snapshot_rank = 1
)
SELECT
        city_name,
        date,
        COUNT(*) AS zone_count,
        MAX(date_maj) AS last_update_at,
        AVG(code_qual) AS avg_quality_code,
        MAX(code_qual) AS max_quality_code,
        ARRAY_AGG(lib_zone IGNORE NULLS ORDER BY code_qual DESC, lib_zone ASC LIMIT 1)[SAFE_OFFSET(0)] AS worst_quality_zone
FROM latest_zone_snapshots
GROUP BY city_name, date
```

Les regles d'agregation a expliquer sont les suivantes. Premiere regle : on combine les sources locales avec UNION ALL, en ajoutant un champ city_name derive du nom de la table source. Cela permet de standardiser des fichiers heterogenes tout en gardant la provenance metier de chaque ligne. Deuxieme regle : on fixe la granularite cible au couple ville plus jour, ce qui permet de comparer les villes a une maille commune. Troisieme regle : si une meme zone remonte plusieurs fois dans une journee, on ne conserve que le snapshot le plus recent grace a ROW_NUMBER partitionne par ville, date et code_zone, puis trie par date_maj decroissante. Quatrieme regle : l'agregation finale combine plusieurs types d'indicateurs, avec COUNT pour le nombre de zones couvertes, MAX pour la date de derniere mise a jour, AVG pour le niveau moyen de pollution, MAX pour le pire niveau atteint, et ARRAY_AGG ordonne pour conserver le libelle ou la zone correspondant a la situation la plus defavorable.

Si le jury me demande une synthese simple, je peux dire : on unionne d'abord les sources ville par ville, on dedoublonne ensuite a l'echelle zone et jour en gardant la mesure la plus recente, puis on consolide au niveau ville plus jour avec des agregats moyens, maxima et libelles representatifs.

### Bloc de code 7 - Aggregation journaliere et indicateurs de qualite de l'air

Source : dbt/models/gold/gold_air_quality_by_city.sql

```sql
WITH ranked_zone_snapshots AS (
    SELECT
        city_name,
        DATE(date_dif) AS date,
        EXTRACT(YEAR FROM DATE(date_dif)) AS annee,
        EXTRACT(MONTH FROM DATE(date_dif)) AS mois,
        EXTRACT(DAY FROM DATE(date_dif)) AS jour,
        date_maj,
        code_zone,
        lib_zone,
        type_zone,
        lib_qual,
        SAFE_CAST(code_qual AS INT64) AS code_qual,
        SAFE_CAST(code_no2 AS INT64) AS code_no2,
        SAFE_CAST(code_o3 AS INT64) AS code_o3,
        SAFE_CAST(code_pm10 AS INT64) AS code_pm10,
        SAFE_CAST(code_pm25 AS INT64) AS code_pm25,
        SAFE_CAST(code_so2 AS INT64) AS code_so2,
        ROW_NUMBER() OVER (
            PARTITION BY city_name, DATE(date_dif), code_zone
            ORDER BY date_maj DESC, lib_zone ASC
        ) AS snapshot_rank
    FROM {{ ref('air_quality_by_city') }}
    WHERE date_dif IS NOT NULL
),

latest_zone_snapshots AS (
    SELECT * EXCEPT(snapshot_rank)
    FROM ranked_zone_snapshots
    WHERE snapshot_rank = 1
)

SELECT
    city_name,
    date,
    annee,
    mois,
    jour,
    COUNT(*) AS zone_count,
    MAX(date_maj) AS last_update_at,
    AVG(code_qual) AS avg_quality_code,
    MAX(code_qual) AS max_quality_code,
    AVG(code_no2) AS avg_no2_code,
    MAX(code_no2) AS max_no2_code,
    AVG(code_o3) AS avg_o3_code,
    MAX(code_o3) AS max_o3_code,
    AVG(code_pm10) AS avg_pm10_code,
    MAX(code_pm10) AS max_pm10_code,
    AVG(code_pm25) AS avg_pm25_code,
    MAX(code_pm25) AS max_pm25_code,
    AVG(code_so2) AS avg_so2_code,
    MAX(code_so2) AS max_so2_code,
    ARRAY_AGG(lib_qual IGNORE NULLS ORDER BY code_qual DESC, lib_zone ASC LIMIT 1)[SAFE_OFFSET(0)] AS worst_quality_label,
    ARRAY_AGG(lib_zone IGNORE NULLS ORDER BY code_qual DESC, lib_zone ASC LIMIT 1)[SAFE_OFFSET(0)] AS worst_quality_zone,
    ARRAY_AGG(type_zone IGNORE NULLS ORDER BY code_qual DESC, lib_zone ASC LIMIT 1)[SAFE_OFFSET(0)] AS worst_quality_zone_type
FROM latest_zone_snapshots
GROUP BY city_name, date, annee, mois, jour
ORDER BY date ASC, city_name ASC
```

Ce bloc remplace l'agrégation energie et CO2 par une logique d'agrégation environnementale. L'idee metier est de garder, pour chaque ville et pour chaque jour, le dernier snapshot disponible par zone, puis de calculer des indicateurs moyens et maxima sur plusieurs polluants. C'est une bonne preuve que le projet sait produire des tables gold non seulement pour l'energie, mais aussi pour des jeux de donnees d'enrichissement.

### Bloc de code 8 - Preparation pour la prediction et pipeline ML

Sources : dbt/models/gold/nat_tr_predi.sql, predict/src/predict/data.py, predict/src/predict/preproc.py et predict/src/predict/model.py

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
def connect_to_bigquery() -> bigquery.Client | None:
    json_credential_file = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS",
        os.path.join(
            os.path.dirname(__file__), "data/meteo/mix-energie-gcp-23501901f9c9.json"
        ),
    )
    project_id = os.getenv("PROJECT_ID")

    if not os.path.exists(json_credential_file):
        get_logger().error(
            f"Fichier de credentials introuvable : {json_credential_file}"
        )
        return None

    credentials = service_account.Credentials.from_service_account_file(
        json_credential_file
    )

    try:
        client = bigquery.Client(project=project_id, credentials=credentials)
    except Exception as e:
        get_logger().error("Fail to connect to project {} : {}".format(project_id, e))
        return None

    return client
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

```python
class Energypredict:
    """
    Class to manage the ML model for predicting energy consumption at T+15 minutes
    """

    __slots__ = ["__model", "__mllogger"]

    def __init__(self, mllogger: pmllog.MlLog):
        self.__model = None
        self.__mllogger = mllogger

    def create_model(self) -> None:
        self.__model = LinearRegression()
        self.__mllogger.log_hyperparams(self.__model.get_params())
        logger.info("Creation of the model")

    def preprocess_data(self, X: pd.DataFrame, train: bool = True) -> pd.DataFrame:
        if train:
            preprocessor = build_pipeline()
            preprocessor.fit(X)
            self.__mllogger.save_model(preprocessor, "preprocessor")
        else:
            preprocessor = self.__mllogger.load_model("preprocessor")
        df_preprocessed = preprocessor.transform(X)
        return df_preprocessed
```

    Ici, je peux montrer le lien entre data engineering et machine learning. dbt prepare des features temporelles propres, puis le module predict applique une pipeline de pretraitement avec imputation KNN et standardisation. J'ajoute aussi la classe Energypredict, qui encapsule la creation du modele, le pretraitement et l'integration avec le logger MLflow. Le module data.py gere de son cote la connexion a BigQuery, puis le chargement des tables gold utilisees pour l'entrainement et l'inference. Le message important a porter est que la prediction n'est pas hors-sol : elle repose sur les tables gold et sur un flux reproductible.

---

## 4. Base de donnees et tracabilite - 2 min

Le choix de BigQuery comme entrepot principal est logique pour ce projet. Nous sommes sur des donnees tabulaires, analytiques, avec une volumetrie raisonnable mais evolutive, et avec un besoin fort de requetage SQL et d'integration native a GCP.

### Schema MCD/MLD a presenter a l'oral

Pour le MCD, je peux presenter le projet comme un ensemble de grandes entites metier reliees par une logique de temps et de territoire.

```text
MCD conceptuel simplifie

VILLE
    1,N -> OBSERVATION_METEO
    1,N -> SNAPSHOT_QUALITE_AIR

ZONE_QUALITE_AIR
    1,N -> SNAPSHOT_QUALITE_AIR

MESURE_ECO2MIX_NATIONALE
    1,N -> AGREGAT_NATIONAL_JOURNALIER
    1,N -> FEATURES_PREDICTION_NATIONALE

MESURE_ECO2MIX_REGIONALE
    1,N -> AGREGAT_REGIONAL_JOURNALIER
    1,N -> FEATURES_PREDICTION_REGIONALE

AGREGAT_NATIONAL_JOURNALIER
    1,1 -> KPI_NATIONAL

SNAPSHOT_QUALITE_AIR
    N,1 -> VILLE
    N,1 -> ZONE_QUALITE_AIR

OBSERVATION_METEO
    N,1 -> VILLE
```

Pour le MLD, je m'appuie sur la structuration physique reelle du projet dans BigQuery et dbt. Le dataset brut correspond au schema cible de dbt, puis dbt cree deux couches analytiques supplementaires, une silver et une gold.

```text
MLD physique simplifie

Dataset raw : PROJECT_ID.DATASET_ID_PROD
    - eco2mix_national_cons_def
    - eco2mix_national_tr
    - eco2mix_regional_cons_def
    - eco2mix_regional_tr
    - meteo_<city>
    - air_quality_<city>
    - _loaded_files

Dataset silver : PROJECT_ID.DATASET_ID_PROD_silver
    - eco2mix_national_cons_def_histo
    - eco2mix_regional_cons_def_histo
    - meteo_by_city
    - air_quality_by_city

Dataset gold : PROJECT_ID.DATASET_ID_PROD_gold
    - nat_cons_agre_j
    - reg_cons_agre_j
    - nat_tr_agre_j
    - reg_tr_agre_j
    - nat_tr_predi
    - reg_tr_predi
    - kpi
    - gold_meteo_by_city
    - gold_air_quality_by_city
```

La logique de lecture est la suivante : les tables raw reçoivent les fichiers charges depuis GCS, les tables silver nettoient et homogénéisent, puis les tables gold exposent des objets orientés usage, soit pour le dashboard, soit pour la prediction.

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

### Bloc de code 10 bis - Script de creation des tables

Sources : ingest_dbt/src/mix_energy/bigquery_loader.py et dbt/models/silver/air_quality_by_city.sql

```python
schema = [
    bigquery.SchemaField("filename", "STRING"),
    bigquery.SchemaField("loaded_at", "TIMESTAMP"),
]
table = bigquery.Table(table_id, schema=schema)
client.create_table(table, exists_ok=True)

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

```sql
{{ config(
    alias='air_quality_by_city',
    materialized='table'
) }}

WITH unioned AS (
    {{ union_city_sources('air_quality_source', 'air_quality_') }}
)

SELECT
    city_name,
    SAFE_CAST(date_maj AS TIMESTAMP) AS date_maj,
    SAFE_CAST(date_dif AS DATE) AS date_dif,
    SAFE_CAST(date_ech AS DATE) AS date_ech
FROM unioned
WHERE SAFE_CAST(date_maj AS TIMESTAMP) IS NOT NULL
```

La bonne explication a donner au jury est qu'il n'existe pas un seul script DDL monolithique dans le projet. La creation physique des tables se fait en deux mecanismes complementaires. D'abord, les tables brutes sont creees techniquement par BigQuery au moment du chargement, avec un schema explicite ou autodetecte via le job de load. Ensuite, les tables analytiques silver et gold sont creees par dbt a partir de modeles SQL materialized en table ou en incremental. C'est un choix plus industriel qu'une suite de CREATE TABLE ecrits a la main.

### Justification du choix technologique : SQL vs NoSQL

Le choix SQL est défendable pour trois raisons principales.

Premiere raison : la nature des donnees. Nous travaillons surtout avec des jeux tabulaires, des timestamps, des mesures numeriques et des dimensions metier stables comme la ville, la zone ou la region. Ce type de donnees se prete tres bien a un entrepot analytique relationnel.

Deuxieme raison : la nature des traitements. Le projet utilise massivement des filtres, des cast typés, des aggregations, des group by, des fenetres analytiques comme ROW_NUMBER, et des calculs journaliers ou ponderes. Ces traitements sont beaucoup plus naturels, lisibles et performants en SQL dans BigQuery qu'en NoSQL documentaire.

Troisieme raison : l'ecosysteme choisi. dbt, BigQuery et l'API generique FastAPI reposent sur l'idee que les jeux de donnees sont exposes sous forme de tables structurees avec des colonnes typées. Un stockage NoSQL aurait ajoute de la flexibilite sur les documents bruts, mais il aurait complique le travail de transformation analytique, la gouvernance des schemas et la production des tables gold.

Si le jury me demande une synthese simple, je peux dire : nous avons choisi SQL parce que notre besoin principal n'est pas de stocker des documents libres, mais de nettoyer, joindre, typer, agreger et exposer des donnees analytiques de maniere fiable et reproductible.

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

### Bloc de code 11 bis - Securisation reelle de l'API

Sources : fastapi/src/mix_energy_api/main.py, fastapi/src/mix_energy_api/config.py et fastapi/src/mix_energy_api/bigquery_service.py

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
default_limit: int = 100
max_limit: int = 1000

safe_limit = (
    self.settings.default_limit
    if limit is None
    else max(1, min(limit, self.settings.max_limit))
)
query_parameters.append(
    bigquery.ScalarQueryParameter("limit_value", "INT64", safe_limit)
)
```

La bonne explication a donner au jury est la suivante : l'API est securisee sur plusieurs niveaux complementaires. Premier niveau, l'API est read-only pour la partie datasets, avec seulement des GET sur la consultation et aucun endpoint d'ecriture sur BigQuery. Deuxieme niveau, le CORS est restrictif et borne les origines autorisees. Troisieme niveau, les entrees sont validees strictement avec Pydantic et les filtres sont converts en requetes parametrees, ce qui limite les erreurs et les injections SQL. Quatrieme niveau, les volumes de donnees sont bornes par default_limit et max_limit pour eviter les appels trop lourds. Cinquieme niveau, une protection optionnelle par cle API peut etre activee par configuration sur les endpoints de consultation et de prediction, ce qui constitue une brique d'industrialisation concrete tout en restant desactivee par defaut pour le developpement local.

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

### Bloc de code 12 bis - Documentation Swagger et OpenAPI

Source : fastapi/src/mix_energy_api/main.py

```python
app = FastAPI(
    title="Mix Energy Dataset API",
    version="0.1.0",
    description="Read-only BigQuery buffer for the Streamlit front-end.",
)
```

FastAPI genere automatiquement la documentation interactive Swagger sur l'URL /docs ainsi que le schema OpenAPI sur /openapi.json, car ces routes ne sont pas desactivees dans create_app. Devant le jury, je peux donc montrer la page /docs pour prouver que les endpoints sont bien documentes, avec leurs parametres, leurs schemas de reponse et leurs statuts HTTP. C'est un point important, parce que la documentation fait partie de la mise a disposition de la donnee, pas seulement du developpement.

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

### Bloc de code 13 bis - Preuve que les donnees sont bien exposees via l'API

Sources : fastapi/README.md et fastapi/tests/unit/test_main.py

```bash
curl http://localhost:8890/tables
curl 'http://localhost:8890/tables?layer=silver'
curl http://localhost:8890/tables/kpi/columns
curl 'http://localhost:8890/tables/air_quality_by_city?layer=silver&limit=10'
curl -X 'POST' 'http://localhost:8890/predict/national' -H 'accept: application/json' -d ''
```

```python
with TestClient(app) as client:
    health_response = client.get("/health", params={"layer": "silver"})
    assert health_response.status_code == 200
    assert health_response.json()["dataset_id"] == "prod_mix_energie_silver"

    tables_response = client.get("/tables", params={"layer": "raw"})
    assert tables_response.status_code == 200
    assert tables_response.json()["dataset_id"] == "prod_mix_energie"
    assert tables_response.json()["tables"] == ["sample_table"]
```

Ce bloc me permet de prouver deux choses. D'une part, la README donne des exemples d'appels concrets qui montrent comment interroger les tables et les endpoints de prediction. D'autre part, les tests unitaires confirment que les endpoints repondent bien en 200 et retournent le dataset attendu selon la couche demandee. Si le jury me demande une preuve simple, je peux dire : je peux ouvrir /docs pour montrer les routes, lancer un curl sur /tables ou /health, et m'appuyer sur les tests pour montrer que l'API repond effectivement avec les bonnes structures.

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

---

## Tableau des ports locaux

| Service   | Port | Usage principal                      |
| --------- | ---: | ------------------------------------ |
| Streamlit | 8501 | Dashboard de visualisation           |
| Airflow   | 8502 | Interface d'orchestration des DAGs   |
| MLflow    | 8503 | Suivi des experiences et des modeles |
| FastAPI   | 8890 | API REST et documentation Swagger    |