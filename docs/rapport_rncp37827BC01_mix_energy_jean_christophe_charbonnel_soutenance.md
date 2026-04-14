# Rapport final de soutenance RNCP37827BC01 - Version personnalisee

## Informations du candidat

- Nom : Charbonnel
- Prenom : Jean-Christophe
- Centre de formation : Artefact
- Ecole / organisme de formation : Artefact
- Composition de l'equipe : Thibault Merville, Xavier Filaire, Kuang Zheng, Candide Hounsou

## Note de personnalisation

Cette version personnalisee du rapport est preparee pour presentation au jury dans le cadre de la certification RNCP37827BC01. Elle reprend le contenu technique du projet Mix Energy en l'associant explicitement au dossier de Jean-Christophe Charbonnel et a l'equipe projet.

# Rapport technique RNCP37827BC01

## Projet

Mix Energy - Plateforme de collecte, transformation, exposition et valorisation de donnees energetiques

## Objet du document

Ce document constitue la version finale du rapport prepare pour la soutenance du projet Mix Energy dans le cadre de la certification RNCP37827BC01. Il a ete concu pour remplir une double fonction : offrir au jury une lecture structurée en amont de la presentation orale et servir de support d'argumentation pendant la soutenance.

Le rapport met en evidence la coherence globale du projet, la profondeur du travail technique realise, la logique d'architecture retenue, la maitrise de la chaine de traitement des donnees et la capacite a relier des choix techniques a un objectif metier clair.

L'ambition du projet est de construire une chaine de valeur complete autour des donnees energetiques francaises : recuperer des donnees heterogenes, les centraliser dans un environnement cloud, les transformer en jeux de donnees exploitables, produire des indicateurs metiers, entrainer des modeles de prediction, exposer le resultat via une API et proposer une visualisation dans un tableau de bord.

## Note de lecture pour la soutenance

Cette version finale est orientee soutenance. Elle doit permettre au jury d'identifier rapidement quatre points essentiels :

- la clarte du besoin metier traite ;
- la coherence de l'architecture de bout en bout ;
- la realite du travail technique visible dans le depot ;
- la capacite du projet a evoluer vers une solution plus complete et industrialisable.

La lecture du document peut ainsi s'effectuer selon un fil directeur simple : comprendre le besoin, observer l'architecture, verifier la realisation, puis mesurer la valeur produite et les perspectives d'evolution.

## 0. Cadrage metier et vision cible du projet

### 0.1 Intitule du projet

Projet Energie - Mix electrique francais et empreinte carbone

### 0.2 Presentation generale

Le projet Mix Energy s'inscrit dans une problematique actuelle a l'intersection de la transition energetique, de la valorisation des donnees et de l'aide a la decision. Il vise a concevoir une chaine de traitement de donnees complete permettant de collecter, structurer, transformer et restituer des informations relatives au mix electrique francais et a son empreinte carbone.

L'objectif est double. D'une part, il s'agit de produire des indicateurs fiables et lisibles sur la production electrique par filiere, la consommation et l'intensite carbone associee. D'autre part, le projet prepare une capacite d'anticipation de la consommation, en commencant par les seules donnees energie puis en envisageant un enrichissement par des donnees meteorologiques historiques et previsionnelles.

Cette partie du document formalise le cadrage metier et la vision cible du projet. Elle complete les preuves techniques presentees plus loin dans le rapport et permet de distinguer ce qui releve du socle deja implemente dans le depot de ce qui constitue une trajectoire d'evolution credibilisee.

### 0.3 Objectif metier

L'objectif metier principal consiste a construire un pipeline de donnees capable d'ingerer des donnees de production electrique par source, telles que le nucleaire, le solaire, l'eolien, le gaz ou l'hydraulique, puis de calculer l'empreinte carbone du mix electrique francais en temps quasi reel, avant de restituer ces informations dans un tableau de bord de suivi national et regional.

A moyen terme, ce socle de donnees a vocation a supporter un cas d'usage predictif plus ambitieux. Il s'agit de mettre en place une estimation de la consommation electrique a J+1. Dans une premiere phase, cette prediction peut s'appuyer exclusivement sur les variables energetiques. Dans une seconde phase, elle peut etre enrichie par des donnees meteorologiques historiques et previsionnelles afin d'ameliorer la qualite des modeles.

### 0.4 Justification du choix du sujet

Le choix de ce projet repose sur plusieurs arguments. Il s'agit d'un cas metier immediatement comprehensible, fortement visuel et directement relie a des enjeux actuels de transition energetique. Il presente egalement un interet professionnel clair pour des recruteurs et acteurs du secteur energie, notamment des entreprises telles que Schneider Electric ou EDF R&D.

Le projet beneficie en outre d'un ecosysteme de sources ouvertes favorable. Les APIs et jeux de donnees mobilises sont publics, documentes, relativement stables et exploitables sans cout d'entree important. Ce contexte rend la demarche techniquement realiste dans un cadre pedagogique tout en conservant une forte valeur demonstrative devant un jury.

### 0.5 Sources de donnees mobilisees ou ciblees

Le projet s'appuie d'abord sur les jeux de donnees Eco2mix diffuses via le portail ODRE. Ces donnees permettent d'acceder aux informations nationales et regionales sur la consommation, la production par filiere, les echanges et certaines estimations associees au systeme electrique. Les jeux eco2mix-national-tr, eco2mix-national-cons-def, eco2mix-regional-tr et eco2mix-regional-cons-def constituent le coeur du dispositif de suivi et d'historisation. Le quota annonce sur ODRE est de 50 000 appels API par utilisateur et par mois, ce qui justifie une orchestration maitrisee des appels.

La Base Carbone ADEME joue un role de referentiel metier. Elle apporte les facteurs d'emission de gaz a effet de serre par filiere de production electrique et permet, par jointure, de convertir les volumes de production en indicateurs d'empreinte carbone.

Dans la vision cible du projet, l'integration de donnees meteorologiques constitue une extension naturelle. Des services comme Open-Meteo permettent de recuperer a la fois des historiques et des previsions de temperature, vent, precipitations et humidite, utiles pour expliquer et predire les variations de consommation electrique.

Une autre extension pertinente consiste a integrer des donnees de qualite de l'air, par exemple via Atmo Data, afin de rapprocher l'intensite carbone du mix electrique et les indicateurs territoriaux de pollution atmospherique. Cette extension renforce la portee analytique du projet sans etre presentee ici comme entierement livree dans le depot actuel.

### 0.6 Architecture fonctionnelle cible

L'architecture fonctionnelle du projet repose sur une logique de pipeline structure en plusieurs temporalites. Une phase d'initialisation permet de constituer le socle historique a partir des donnees consolidees nationales et regionales ainsi que du referentiel carbone. Une phase recurrente alimente ensuite les donnees du jour ou du mois via les jeux temps reel et les traitements correctifs. Enfin, les transformations analytiques permettent de produire des tables orientees usage pour le suivi, le calcul de KPIs et la prediction.

Dans cette vision cible, un DAG Airflow quotidien ou infra-journalier alimente les donnees temps reel, tandis qu'un DAG mensuel ou periodique remplace les donnees provisoires par les versions consolidees lorsqu'elles deviennent disponibles. Les transformations dbt servent ensuite a produire les tables de restitution, les croisements analytiques et les jeux de donnees prets pour les usages machine learning.

### 0.7 Exemple d'appel API

L'acces aux jeux de donnees ODRE peut etre realise via une requete HTTP parametree. L'exemple suivant illustre le principe general d'interrogation des jeux Eco2mix et justifie le choix d'une couche d'ingestion Python legere, reposant sur requests.

```python
import requests

BASE_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets"


def get_eco2mix(dataset: str, limit: int = 100) -> dict:
    url = f"{BASE_URL}/{dataset}/records"
    params = {
        "limit": limit,
        "order_by": "date_heure desc",
        "timezone": "Europe/Paris",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


national_tr = get_eco2mix("eco2mix-national-tr")
national_def = get_eco2mix("eco2mix-national-cons-def")
regional_tr = get_eco2mix("eco2mix-regional-tr")
regional_def = get_eco2mix("eco2mix-regional-cons-def")
```

### 0.8 Architecture technique cible et couverture RNCP

Sur le plan technique, le projet repose sur une architecture modulaire articulee autour de plusieurs composants specialises : ingestion Python, stockage intermediaire dans GCP Storage, transformations dbt, stockage analytique dans BigQuery, orchestration Airflow, exposition des donnees via FastAPI et restitution dans Streamlit. L'infrastructure GCP et le provisioning Terraform donnent a cette chaine une dimension industrialisable.

Dans la cible d'architecture complete, des briques supplementaires peuvent renforcer le dispositif, notamment des controles de qualite de donnees formalises, une chaine CI/CD et des enrichissements multi-sources autour de la meteo et de la qualite de l'air. Ces composants sont presentes comme extensions ou feuille de route lorsque leur implementation n'est pas integralement visible dans le depot actuel.

Le projet presente enfin un fort alignement avec les attendus pedagogiques et RNCP. Il couvre l'extraction automatisee de donnees multi-sources, la structuration et l'homogeneisation des jeux de donnees, les transformations analytiques SQL, l'orchestration de pipelines, l'exposition de services REST et la restitution visuelle dans un dashboard. Cette articulation renforce la lisibilite du projet pour un jury et valorise sa coherence de bout en bout.

## 1. Contexte et problematique

Le secteur de l'energie est fortement dependent de la disponibilite de donnees fiables, regulieres et interpretables. Les donnees de production, de consommation, d'emissions et de contexte exogene comme la meteo ou la qualite de l'air doivent etre rapprochées pour permettre des analyses utiles et des predictions court terme.

Le projet Mix Energy repond a plusieurs besoins concrets :

- centraliser des donnees provenant de plusieurs sources ouvertes ;
- historiser ces donnees dans un environnement analytique exploitable ;
- construire des tables consolidees orientees usage metier ;
- produire des indicateurs de pilotage, notamment sur le mix energetique et le CO2 ;
- preparer des donnees pour la prediction de consommation ;
- entrainer des modeles de machine learning pour l'anticipation des besoins ;
- exposer les donnees dans une API fiable et reutilisable ;
- proposer une interface de visualisation orientee lecture et analyse.

Le travail de fond ne se limite donc pas a une application unique. Il couvre l'ensemble du cycle de vie de la donnee, depuis l'ingestion jusqu'a la restitution visuelle, avec une logique de production et de deploiement.

## 2. Presentation generale de la solution

Le depot est organise en plusieurs briques complementaires :

- Airflow pour l'orchestration des flux et le declenchement des traitements ;
- dbt pour la transformation SQL et la structuration des couches analytiques ;
- FastAPI pour l'exposition read-only des donnees consolidees ;
- Streamlit pour la visualisation et la navigation dans les indicateurs ;
- un module de prediction en Python pour l'entrainement des modeles ;
- Terraform pour l'infrastructure GCP ;
- des tests unitaires pour valider les composants critiques.

Cette decomposition montre une approche modulaire du projet. Chaque composant a une responsabilite claire, ce qui facilite la maintenance, la lisibilite et la possibilite de faire evoluer le systeme.

## 3. Architecture technique

L'architecture technique repose sur une chaine de traitement en couches.

### 3.1 Couche ingestion et orchestration

Les DAGs Airflow presents dans le dossier airflow/dags pilotent les traitements. Ils assurent notamment :

- la verification de la disponibilite du bucket de stockage ;
- l'ingestion des fichiers CSV depuis des jeux de donnees externes ;
- le transfert des fichiers vers BigQuery ;
- le declenchement des transformations dbt ;
- l'entrainement des modeles de prediction.

Les fichiers les plus representatifs sont :

- airflow/dags/dag_base_carbone.py
- airflow/dags/dag_eco2mix_national_tr.py
- airflow/dags/dag_eco2mix_national_cons_def.py
- airflow/dags/dag_eco2mix_regional_tr.py
- airflow/dags/dag_eco2mix_regional_cons_def.py
- airflow/dags/dag_train_model.py

### 3.2 Couche stockage et transformation

Les donnees sont chargees dans BigQuery puis transformeес via dbt. Le projet dbt distingue au minimum deux couches de travail :

- une couche silver pour nettoyer, typer et homogeniser ;
- une couche gold pour agreger, calculer les indicateurs et preparer les donnees de prediction.

Cette separation est importante. Elle montre un travail de structuration analytique et non un simple empilement de scripts.

### 3.3 Couche exposition

Le service FastAPI fournit une couche d'acces standardisee aux donnees consolidees. L'API permet de :

- lister les tables disponibles ;
- lister les colonnes d'une table ;
- interroger une table avec des filtres et une limite.

Cette couche sert d'interface entre le stockage analytique et le front. Elle contribue a decoupler la presentation des mecanismes internes de stockage.

### 3.4 Couche presentation

Le front Streamlit propose plusieurs vues :

- historique national ;
- temps reel national ;
- historique regional ;
- temps reel regional.

Le front n'est pas un simple prototype. Le code montre un travail de structuration de pages, de style, et de chargement cible des donnees via l'API.

### 3.5 Couche infrastructure et deploiement

Le dossier iac contient une infrastructure as code Terraform pour Google Cloud Platform. On y trouve notamment :

- la creation du projet GCP ;
- l'activation des services cloud ;
- la creation de comptes de service dedies ;
- la creation d'un bucket GCS ;
- la mise en place d'Artifact Registry ;
- l'attribution de roles IAM adaptes.

Cela renforce la dimension professionnelle du projet : le systeme n'est pas seulement developpe localement, il est pense pour etre deploie et administre.

## 4. Flux de donnees de bout en bout

Le flux principal du projet peut etre resume ainsi :

1. recuperation de donnees externes ;
2. depot dans un bucket GCS ;
3. chargement vers BigQuery ;
4. transformation dbt vers des tables analytiques ;
5. exploitation pour les KPIs et la prediction ;
6. exposition via FastAPI ;
7. consommation via Streamlit.

Ce flux de bout en bout constitue un point fort du projet. Il demontre une capacite a traiter un besoin data complet et pas uniquement une brique isolee.

## 5. Travail realise sur l'ingestion des donnees

Le module d'ingestion contient une logique reelle de communication avec des sources externes. Le fichier ingest_dbt/src/mix_energy/eco2mix_ingest.py montre par exemple :

- la construction d'URL vers l'API de donnees ouverte ;
- la gestion explicite des codes HTTP 200, 400, 401, 429 et 500 ;
- la recuperation des exports CSV ;
- la selection d'enregistrements pour certains usages ;
- le chargement ulterieur vers le bucket.

Cette gestion prouve que le travail ne s'est pas limite a un cas ideal. Les erreurs reseau et les statuts de retour sont pris en compte.

### Extrait de code 1 - Gestion de la reponse HTTP

```python
result = requests.get(req_url, params=params)
match result.status_code:
    case 200:
        logger.info(
            "Successful connection to {} to retrieve CSV file   ".format(base_url)
        )
    case 400:
        logger.error("Bad request {} with params {}".format(req_url, params))
    case 401:
        logger.error(
            "Unauthorized  access to {} with params {}".format(req_url, params)
        )
    case 429:
        json_res = result.json()
        if "errorcode" in json_res:
            logger.error(
                "Errorcode : {} - {}, limit :{} / {} ".format(
                    json_res["errorcode"],
                    json_res["error"],
                    json_res["call_limit"],
                    json_res["limit_time_unit"],
                )
            )
        return {}
```

Cet extrait est important parce qu'il montre une logique defensive et une prise en compte des limitations d'API, notamment le rate limiting.

## 6. Orchestration Airflow

Les DAGs structurent le traitement. Ils combinent verification de connexion, ingestion, transfert vers BigQuery et execution de commandes dbt. Le code montre aussi des horaires de declenchement precis, adaptes au type de donnees.

### Extrait de code 2 - Entrainement des modeles via Airflow

```python
@dag(
    dag_id="dag_train_model",
    description="Entraine les modeles de machine learning pour la prediction de consommation d'energie.",
    start_date=datetime(2026, 1, 1),
    schedule=MultipleCronTriggerTimetable(
        "10 12 2 * 1-5",
        "10,15 12 2 * 1",
        "10 12 2 * 1",
        timezone="Europe/Paris",
    ),
    catchup=False,
    tags=["ml-model", "training"],
)
def dag_train_model():
    @task(task_id="check_bigquery_connection")
    def check_bigquery_connection() -> None:
        bq_hook = BigQueryHook(gcp_conn_id=GCP_CONN_ID, use_legacy_sql=False)
        print("Check Bigquery connection")
```

Cet extrait montre plusieurs elements de fond :

- l'usage d'une orchestration formelle ;
- une planification non triviale ;
- la verification prealable de la disponibilite des ressources ;
- la prise en compte de la couche BigQuery dans le pipeline ML.

## 7. Transformations analytiques avec dbt

L'une des preuves les plus fortes du travail de fond se trouve dans les modeles SQL dbt. Les fichiers du dossier dbt/models/gold montrent que les donnees ne sont pas seulement stockees mais structurees pour l'analyse et la prediction.

Le modele dbt reg_tr_predi.sql prepare par exemple des variables de travail a partir d'historiques de consommation. On y trouve des fenetres analytiques, des extractions temporelles et des moyennes glissantes.

### Extrait de code 3 - Feature engineering SQL

```sql
SELECT
code_insee_region,
date_heure,
consommation,
IFNULL(AVG(consommation) OVER (
  PARTITION BY code_insee_region
  ORDER BY date_heure asc
  ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
),0) AS prev_conso_mean,
IFNULL(AVG(consommation) OVER (
  PARTITION BY code_insee_region
  ORDER BY date_heure asc
  ROWS BETWEEN 4 PRECEDING AND 1 PRECEDING
),0) AS prev_conso_mean_h,
IFNULL(AVG(consommation) OVER (
  PARTITION BY code_insee_region
  ORDER BY date_heure asc
  ROWS BETWEEN 2880 PRECEDING AND 1 PRECEDING
),0) AS prev_conso_mean_m,
EXTRACT(YEAR FROM date_heure) AS year,
EXTRACT(MONTH FROM date_heure) AS month,
EXTRACT(DAY FROM date_heure) AS day,
EXTRACT(HOUR FROM date_heure) AS hour,
EXTRACT(MINUTE FROM date_heure) AS minute
FROM {{ source('reg_source', 'eco2mix_regional_tr') }}
```

Cet extrait prouve plusieurs competences :

- maitrise des fonctions analytiques SQL ;
- capacite a preparer des variables pertinentes pour le machine learning ;
- structuration d'une chaine de transformation reproductible.

Le modele kpi.sql montre en outre une logique metier orientee usage.

### Extrait de code 4 - Calcul d'indicateurs metier

```sql
select
SUM(production) AS production_totale,
SUM(nucleaire) / SUM(production) AS pct_nucleaire,
SUM(fioul + charbon + gaz) / SUM(production) AS pct_thermique,
SUM(eolien + solaire + hydraulique + bioenergies) / SUM(production) AS pct_renouvelable,
SUM(taux_co2 * production) / SUM(production) AS taux_co2
from {{ref('nat_cons_agre_j')}}
```

Ce calcul relie directement la technique a une lecture metier du mix energetique.

## 8. Exposition des donnees via FastAPI

Le service FastAPI n'est pas uniquement un point d'entree minimal. Le code montre une API bien structuree, avec :

- un chargement de configuration dedie ;
- une initialisation du service a l'ouverture ;
- des schemas de validation ;
- une gestion propre des erreurs ;
- des filtres dynamiques sur les requetes.

### Extrait de code 5 - Parsing et validation des filtres

```python
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
```

Ce point est important pour un projet professionnalisant : les entrees utilisateurs sont controlees et les erreurs remontees proprement.

Le service BigQuery montre aussi une vraie attention a la securisation des requetes.

### Extrait de code 6 - Construction de filtres BigQuery securises

```python
return (
    f"{field_name} {sql_operator} @{parameter_name}",
    [
        _coerce_query_parameter(
            bigquery,
            parameter_name,
            column.field_type,
            filter_clause.value,
        )
    ],
)
```

L'usage de parametres plutot que d'une concatenation naive des valeurs est un bon indicateur de maturite technique.

## 9. Frontend Streamlit et restitution

Le front Streamlit propose une navigation entre plusieurs pages thematiques. Le code de la page d'accueil montre un travail de presentation, de structuration et de separation des responsabilites.

Le front charge les donnees a la demande, page par page, ce qui limite le cout de chargement initial. Cela montre une reflexion sur les performances et l'ergonomie.

Le tableau de bord n'est donc pas seulement demonstratif : il sert de couche de lecture fonctionnelle au-dessus de l'API.

## 10. Prediction et machine learning

Le dossier predict constitue une brique autonome du projet. Il repose notamment sur :

- scikit-learn ;
- mlflow ;
- un pretraitement dedie ;
- un modele de regression lineaire ;
- des metriques d'evaluation.

### Extrait de code 7 - Entrainement et evaluation du modele

```python
X_train, X_test, y_train, y_test = create_X_y(
    df, test_size=test_size, random_state=random_state
)

X_train_preproc = predicteng.preprocess_data(X_train, train=True)
X_test_preproc = predicteng.preprocess_data(X_test, train=False)

predicteng.create_model()
predicteng.train_model(X_train=X_train_preproc, y_train=y_train)
predicteng.evaluate_model(X_test=X_test_preproc, y_test=y_test)
```

### Extrait de code 8 - Metriques suivies

```python
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
mape = mean_absolute_percentage_error(y_test, y_pred)
metrics = {"mae": mae, "mse": mse, "r2": r2, "mape": mape}
self.__mllogger.log_metrics(metrics)
```

Ces extraits montrent que le projet integre un vrai cycle ML : preparation des donnees, entrainement, evaluation, journalisation et reutilisation des artefacts.

## 11. Infrastructure as Code et industrialisation

L'infrastructure est decrite via Terraform. Le fichier iac/main.tf montre un niveau de detail significatif : projet GCP, services, comptes de service, bucket, registres d'artefacts et droits IAM.

### Extrait de code 9 - Activation de services cloud

```hcl
resource "google_project_service" "compute" {
  project            = google_project.mix_energie_gcp.project_id
  service            = "compute.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "bigquery" {
  project            = google_project.mix_energie_gcp.project_id
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "storage" {
  project            = google_project.mix_energie_gcp.project_id
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}
```

### Extrait de code 10 - Comptes de service dedies

```hcl
resource "google_service_account" "fastapi_mix_energie" {
  count        = var.TF_VAR_bootstrap_only ? 0 : 1
  project      = google_project.mix_energie_gcp.project_id
  account_id   = "fastapi-mix-energie"
  description  = "Service account dedie a l'application FastAPI mix-energie."
}

resource "google_service_account" "airflow_mix_energie" {
  count        = var.TF_VAR_bootstrap_only ? 0 : 1
  project      = google_project.mix_energie_gcp.project_id
  account_id   = "airflow-mix-energie"
  description  = "Service account dedie a Airflow pour consommer les artefacts du projet."
}
```

Ce volet infrastructure renforce tres clairement la valeur du projet pour la certification. Il montre une capacite a penser exploitation, securite et deploiement.

## 12. Qualite logicielle et tests

Le depot contient des tests unitaires dans plusieurs sous-projets. Cette presence est importante car elle montre un souci de verification et de robustesse.

Exemples de fichiers :

- fastapi/tests/unit/test_bigquery_service.py
- ingest_dbt/tests/unit/test_eco2mix_ingest.py
- ingest_dbt/tests/unit/test_bigquery_loader.py
- ingest_dbt/tests/unit/test_dag_eco2mix_national_tr.py
- ingest_dbt/tests/unit/test_dag_eco2mix_regional_tr.py

### Extrait de code 11 - Test de requete BigQuery securisee

```python
result = service.query_table(
    "daily_stats",
    columns=["day", "region"],
    filters=[
        FilterClause(field="region", operator="eq", value="FR"),
        FilterClause(field="value", operator="gte", value=1.0),
    ],
    limit=25,
)

sql, job_config = service.client.queries[0]
assert "WHERE `region` = @filter_0 AND `value` >= @filter_1" in sql
assert "LIMIT @limit_value" in sql
```

### Extrait de code 12 - Test de limitation API cote ingestion

```python
result = eco2mix.__perform_request("https://example.com", params={"foo": "bar"})
assert result == {}
```

Ces tests montrent que des scenarios non nominaux ont ete pris en compte. C'est un argument important pour prouver le serieux du travail produit.

## 13. Competences mobilisees et adequation avec le bloc RNCP

Au regard du contenu du depot et de l'architecture, plusieurs competences attendues dans un bloc de certification de type RNCP sont mobilisees :

- analyse d'un besoin et decoupage en sous-systemes ;
- conception d'une architecture logicielle modulaire ;
- developpement Python back-end ;
- traitement et preparation de donnees ;
- modelisation analytique SQL ;
- orchestration de flux de traitement ;
- exposition de services API ;
- conception d'une interface de restitution ;
- mise en place de tests ;
- infrastructure as code et deploiement cloud.

Ce point est essentiel pour le jury : le projet ne repose pas sur une seule competence, mais sur une articulation entre developpement, data engineering, API, visualisation, machine learning et DevOps.

## 14. Difficultes techniques et enjeux reussis

Au vu de la structure du projet, plusieurs difficultes techniques ont ete traitees :

- heterogeneite des sources de donnees ;
- synchronisation de traitements dependants ;
- gestion de l'exposition securisee des donnees analytiques ;
- preparation de features temporelles pertinentes ;
- conservation d'une architecture lisible malgre la multiplicite des briques ;
- industrialisation de l'environnement cible dans GCP.

La qualite du depot montre que le projet a ete pense sur la duree, avec une logique de structuration progressive.

## 15. Resultats et valeur produite

Le projet Mix Energy produit plusieurs resultats concrets :

- une chaine de collecte et de transformation exploitable ;
- des tables analytiques orientees metier ;
- un calcul de KPIs autour de la production, du mix et du CO2 ;
- une API de consultation des donnees ;
- une interface utilisateur de restitution ;
- une base technique pour des predictions de consommation ;
- une infrastructure de deploiement cloud.

Ces livrables montrent une coherence de bout en bout. Le projet ne se limite pas a un exercice de code : il correspond a un systeme d'information data complet, structure et industrialisable.

## 16. Conclusion de soutenance

Le projet Mix Energy constitue une demonstration solide de capacite a concevoir, implementer et structurer une solution data complete dans un contexte proche des attentes du monde professionnel. Il ne s'agit pas d'un assemblage de composants isoles, mais d'un systeme coherent qui relie ingestion de donnees, orchestration, transformation analytique, exposition de services, restitution visuelle, prediction et infrastructure cloud.

Ce qui donne sa force a ce projet dans le cadre d'une soutenance est la convergence entre trois dimensions. La premiere est la lisibilite metier : le sujet est compréhensible, actuel et directement relie a des enjeux energetiques et environnementaux concrets. La deuxieme est la profondeur technique : le depot montre un travail reel sur les pipelines, les transformations SQL, les DAGs Airflow, l'API FastAPI, la couche de visualisation et l'infrastructure GCP. La troisieme est la credibilite d'evolution : le projet dispose deja d'un socle fonctionnel et technique suffisamment structure pour accueillir des extensions autour de la meteo, de la qualite de l'air, de la prediction a J+1 et de l'industrialisation continue.

Dans une logique de certification RNCP37827BC01, ce dossier demontre donc bien plus qu'une capacite a coder. Il met en evidence une demarche complete d'analyse, de conception, d'integration, de structuration des donnees, de mise a disposition de services et de projection vers une solution exploitable a plus grande echelle.

En conclusion, Mix Energy peut etre presente au jury comme un projet a la fois utile, coherent, techniquement defendable et pedagogiquement representatif des competences attendues. Il apporte une preuve concrete de travail de fond, de capacite d'industrialisation et d'aptitude a transformer un besoin metier en solution data argumentee de bout en bout.

## 17. Annexes - fichiers principaux du depot

### Composants orchestration

- airflow/dags/dag_base_carbone.py
- airflow/dags/dag_eco2mix_national_tr.py
- airflow/dags/dag_eco2mix_national_cons_def.py
- airflow/dags/dag_eco2mix_regional_tr.py
- airflow/dags/dag_eco2mix_regional_cons_def.py
- airflow/dags/dag_train_model.py
- airflow/docker-compose.yaml

### Composants data

- ingest_dbt/src/mix_energy/eco2mix_ingest.py
- ingest_dbt/src/mix_energy/base_carbone_ingest.py
- ingest_dbt/src/mix_energy/bucket_to_bigquery_airflow.py
- dbt/models/silver/eco2mix_national_cons_def_histo.sql
- dbt/models/silver/eco2mix_regional_cons_def_histo.sql
- dbt/models/gold/nat_cons_agre_j.sql
- dbt/models/gold/nat_tr_agre_j.sql
- dbt/models/gold/nat_tr_predi.sql
- dbt/models/gold/reg_cons_agre_j.sql
- dbt/models/gold/reg_tr_agre_j.sql
- dbt/models/gold/reg_tr_predi.sql
- dbt/models/gold/kpi.sql

### API et front

- fastapi/src/mix_energy_api/main.py
- fastapi/src/mix_energy_api/bigquery_service.py
- fastapi/src/mix_energy_api/schemas.py
- front-streamlit/dashboard/dashboard_app.py
- front-streamlit/dashboard/data_api_client.py
- front-streamlit/dashboard/pages/1_national_historique.py
- front-streamlit/dashboard/pages/2_national_temps_reel.py
- front-streamlit/dashboard/pages/3_regional_historique.py
- front-streamlit/dashboard/pages/4_regional_temps_reel.py

### Prediction et infrastructure

- predict/src/predict/train.py
- predict/src/predict/model.py
- predict/src/predict/preproc.py
- iac/main.tf
- iac/provider.tf
- iac/variables.tf
