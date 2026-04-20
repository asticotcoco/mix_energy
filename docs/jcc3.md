# Script oral de soutenance 20 minutes

## Candidat

- Nom : Charbonnel
- Prenom : Jean-Christophe
- Centre de formation : Artefact
- Projet : Mix Energy
- Bloc : RNCP37827BC01

## Intention du document

Ce script reprend l'esprit du PDF modele JobMatch : une progression tres structuree, un angle technique clair, et des extraits de code relies a des etapes precises du pipeline.

L'objectif n'est pas de lire ce document mot a mot. Il sert de trame orale pour tenir 20 minutes avec un discours maitrise, concret, et defendable devant le jury.

Le fil directeur est simple : partir du besoin metier, montrer l'architecture de bout en bout, puis prouver les choix techniques a partir de blocs de code reels du projet.

## Decoupage cible

- Introduction et promesse du projet : 1 min 30
- Vue d'ensemble architecturale : 2 min
- Collecte automatisee et robustesse d'ingestion : 2 min 30
- Orchestration Airflow : 2 min
- Transformation analytique avec dbt : 2 min 30
- Exposition des donnees via FastAPI : 2 min 30
- Consommation API cote dashboard : 1 min 30
- Prediction et apprentissage automatique : 2 min 30
- Infrastructure Terraform et industrialisation : 1 min 30
- Qualite, limites, conclusion : 1 min 30

## Conseils d'usage

Garder un debit calme. Marquer une pause entre les chapitres. Quand un bloc de code apparait a l'ecran, ne pas le lire ligne par ligne : expliquer la logique, le risque traite, et la valeur apportee.

---

## 1. Introduction et promesse du projet - 1 min 30

Bonjour, je vais vous presenter le projet Mix Energy, realise dans le cadre du bloc RNCP37827BC01.

L'objectif de ce projet etait de construire une chaine data complete autour du mix electrique francais. Concretement, nous voulions recuperer des donnees ouvertes de production et de consommation, les historiser, les transformer, calculer des indicateurs metier comme les parts de production par filiere et l'intensite carbone, puis exposer ces donnees dans une API et un dashboard.

Le projet ne s'arrete pas a la visualisation. Nous avons aussi prepare une brique predictive pour estimer la consommation a court terme. Cela donne au projet une dimension plus interessante qu'un simple reporting : on ne fait pas seulement de la restitution, on prepare aussi de l'anticipation.

Ce que je vais montrer aujourd'hui, c'est surtout la coherence d'ensemble. Mon enjeu n'est pas de presenter une juxtaposition d'outils, mais de demontrer qu'il existe ici une vraie architecture de pipeline data, avec ingestion, orchestration, transformation, exposition, consommation et industrialisation.

La lecture de ma soutenance suivra donc une logique de bout en bout, avec des preuves concretes dans le code du depot.

---

## 2. Vue d'ensemble architecturale - 2 min

Sur le plan metier, le sujet est simple a comprendre : suivre le mix electrique francais, mesurer la consommation, rapprocher ces donnees de facteurs d'emission carbone, puis les rendre lisibles a travers une interface d'analyse. Cela donne immediatement de la valeur au projet, parce que les enjeux energie, sobriete, pilotage et anticipation sont actuels et facilement explicables.

Sur le plan technique, l'architecture repose sur plusieurs briques specialisees. L'ingestion Python interroge les sources externes, notamment les jeux Eco2mix. Airflow orchestre les traitements et structure les dependances. Le stockage analytique repose sur BigQuery. dbt construit les couches de transformation, en separant les tables brutes, les tables nettoyees et les tables de restitution. FastAPI expose les jeux consolides sous forme de service read-only. Streamlit consomme cette API pour afficher les donnees. Enfin, un module de prediction vient completer le dispositif, et Terraform gere l'infrastructure GCP.

Ce decoupage est important devant le jury, car il montre une logique d'architecture et de responsabilites. Chaque composant a un role clair. Cela facilite la maintenance, les evolutions, les tests, et la lisibilite du systeme.

Si je devais resumer le projet en une phrase, je dirais que Mix Energy est une chaine data de bout en bout pour transformer des donnees energiques heterogenes en indicateurs exploitables et en services reutilisables.

---

## 3. Collecte automatisee et robustesse d'ingestion - 2 min 30

La premiere preuve de travail de fond se situe au niveau de l'ingestion. Dans beaucoup de projets, cette partie est reduite a un simple appel API heureux. Ici, le code traite explicitement les statuts HTTP, les problemes d'autorisation, les limitations de quota et les erreurs serveur. C'est un point important, parce qu'un pipeline ne vaut rien si son entree est fragile.

### Bloc de code 1 - Gestion defensive des appels HTTP

Source : ingest_dbt/src/mix_energy/eco2mix_ingest.py

```python
def __perform_request(req_url: str, params: dict):
    result = requests.get(req_url, params=params)
    match result.status_code:
        case 200:
            logger.info(
                "Successful connection to {} to retrieve CSV file   ".format(base_url)
            )

        case 400:
            logger.error("Bad request {} with params {}".format(req_url, params))
            json_res = result.json()
            logger.error(json_res["message"])

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

Quand je montre ce bloc, j'explique que nous avons choisi une approche defensive. On voit que le code ne suppose pas que la source externe est toujours disponible ou toujours correcte. Il prend en charge les retours 400, 401, 429 et 500. Cela veut dire que nous avons pense la collecte comme une brique de production, pas comme un simple notebook exploratoire.

J'insiste aussi sur le fait que le projet sait travailler avec des exports CSV, ce qui simplifie ensuite les chargements vers le stockage et BigQuery. Cela correspond bien a une logique ELT pragmatique : recuperer une matiere brute fiable, la deposer, puis transformer en aval.

Cette partie me permet de montrer au jury que le pipeline est robuste des la premiere etape, et que le traitement des erreurs n'a pas ete laisse de cote.

---

## 4. Orchestration Airflow - 2 min

Une fois les donnees recuperables, encore faut-il organiser les traitements. C'est le role d'Airflow. Les DAGs du projet ne servent pas seulement a lancer des scripts : ils structurent les prerequis, les transferts, les verifications et le declenchement des transformations analytiques.

### Bloc de code 2 - DAG d'ingestion nationale temps reel

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
    @task(task_id="check_bucket_connection")
    def check_bucket_connection() -> str:
        hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        try:
            hook.list(bucket_name=BUCKET_NAME, max_results=1)
        except Exception as exc:
            raise RuntimeError("Connexion au bucket GCP impossible.") from exc
        return BUCKET_NAME

    @task(task_id="ingest_csv_to_bucket")
    def ingest_csv_to_bucket(bucket_name: str, dataset_id: str) -> None:
        csv_content = _retrieve_csv(dataset_id=dataset_id)
        if csv_content is None:
            raise RuntimeError(f"Recuperation CSV echouee pour {dataset_id}.")

    (
        check_bucket_connection_task
        >> ingest_csv_to_bucket_task
        >> transfer_csv_from_bucket_to_bigquery_task
        >> check_dbt_target_datasets_task
        >> dbt_eco2mix_national_tr
    )
```

Ce que je souligne ici, c'est la logique de chaine. On commence par verifier le bucket, puis on ingere, puis on transfere vers BigQuery, puis on controle les datasets dbt cibles, et enfin on lance la transformation. La dependance explicite entre les taches rend le pipeline lisible et monitorable.

Le schedule lui-meme est interessant, car il traduit un besoin de suivi regulier pendant les heures utiles. On n'est pas sur un cron arbitraire : on est deja dans une logique d'exploitation.

Ce bloc me permet donc de montrer que l'orchestration n'est pas un detail. Elle est le squelette du projet.

---

## 5. Transformation analytique avec dbt - 2 min 30

La deuxieme grande preuve de maturite se trouve dans dbt. Le projet ne se contente pas de stocker des fichiers ou des tables brutes. Il construit des modeles analytiques lisibles, versionnes, et relies a des usages metier.

Je peux expliquer ici la logique medaillon en restant simple : les donnees brutes arrivent dans les sources, une couche de travail les nettoie et les type, puis une couche gold expose des tables orientees usage, par exemple pour les KPIs ou la prediction.

### Bloc de code 3 - Table de preparation pour la prediction nationale

Source : dbt/models/gold/nat_tr_predi.sql

```sql
WITH source_rows AS (
    SELECT
        {{ safe_float64_from_raw('consommation') }} AS consommation,
        {{ safe_float64_from_raw('prevision_j1') }} AS prevision_j1,
        {{ safe_float64_from_raw('prevision_j') }} AS prevision_j,
        SAFE_CAST(date_heure AS TIMESTAMP) AS date_heure
    FROM {{ source('nat_source', 'eco2mix_national_tr') }}
)

SELECT
consommation,
prevision_j1,
prevision_j,
EXTRACT(YEAR FROM date_heure) AS year,
EXTRACT(MONTH FROM date_heure) AS month,
EXTRACT(DAY FROM date_heure) AS day,
EXTRACT(HOUR FROM date_heure) AS hour,
EXTRACT(MINUTE FROM date_heure) AS minute
FROM source_rows
WHERE date_heure IS NOT NULL
  AND EXTRACT(YEAR FROM date_heure) = EXTRACT(YEAR FROM CURRENT_DATE())
  AND consommation IS NOT NULL
order by date_heure asc
```

Quand j'affiche ce SQL, j'explique que la transformation ne sert pas seulement a nettoyer : elle sert a preparer des variables directement exploitables par les usages aval. Ici, on convertit les champs, on cast le timestamp, puis on derive year, month, day, hour et minute. Autrement dit, on transforme un flux brut en jeu de donnees utile pour la prediction.

### Bloc de code 4 - Calcul d'un KPI metier

Source : dbt/models/gold/kpi.sql

```sql
select
SUM(production) AS production_totale,
SUM(nucleaire) / SUM(production) AS pct_nucleaire,
SUM(fioul + charbon + gaz) / SUM(production) AS pct_thermique,
SUM(eolien + solaire + hydraulique + bioenergies) / SUM(production) AS pct_renouvelable,
SUM(taux_co2 * production) / SUM(production) AS taux_co2
from {{ref('nat_cons_agre_j')}}
```

Ce deuxieme bloc montre l'autre versant de dbt : la production d'indicateurs metier. On ne parle plus seulement de colonnes techniques. On calcule des parts de nucleaire, de thermique, de renouvelable, et un taux carbone moyen. C'est exactement le moment ou la donnee brute devient information decisionnelle.

Ce chapitre est souvent fort devant un jury, parce qu'il prouve le passage entre extraction et valeur metier.

---

## 6. Exposition des donnees via FastAPI - 2 min 30

Une fois les donnees preparees, il faut les rendre consommables proprement. Nous aurions pu faire parler le front directement a BigQuery, mais ce choix aurait cree un couplage fort, plus de complexite de configuration et moins de controle sur les requetes. C'est pour cela que nous avons intercale une API FastAPI en lecture seule.

### Bloc de code 5 - Endpoint generique de consultation de table

Source : fastapi/src/mix_energy_api/main.py

```python
@app.get("/tables/{table_name}", response_model=QueryResponse)
def query_table(
    request: Request,
    table_name: str,
    columns: str | None = Query(
        default=None, description="Comma-separated list of columns"
    ),
    filters: str | None = Query(
        default=None,
        description="JSON array of filter clauses",
    ),
    layer: DatasetLayer = Query(default="gold"),
    limit: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    service = get_service(request, layer=layer)
    parsed_columns = _parse_columns(columns)
    parsed_filters = _parse_filters(filters)

    try:
        return service.query_table(
            table_name,
            columns=parsed_columns,
            filters=parsed_filters,
            limit=limit,
        )
```

Ici, j'explique que l'API n'est pas ecrite endpoint par endpoint pour chaque tableau. Elle propose un acces plus generique, mais borne, au contenu des datasets. Cela permet au front d'interroger plusieurs tables, plusieurs couches, et plusieurs filtres sans dupliquer toute la logique metier.

J'insiste aussi sur la validation des entrees. Les colonnes et les filtres sont parses avant execution. Cela montre que l'API n'est pas une simple passerelle brute.

### Bloc de code 6 - Construction d'une requete BigQuery bornee et parametree

Source : fastapi/src/mix_energy_api/bigquery_service.py

```python
safe_limit = (
    self.settings.default_limit
    if limit is None
    else max(1, min(limit, self.settings.max_limit))
)
query_parameters.append(
    bigquery.ScalarQueryParameter("limit_value", "INT64", safe_limit)
)

select_columns_sql = ", ".join(f"`{name}`" for name in selected_column_names)
query_sql = (
    f"SELECT {select_columns_sql} FROM `{self.dataset_fqn}.{table.name}`"
)
if where_clauses:
    query_sql += " WHERE " + " AND ".join(where_clauses)
query_sql += " LIMIT @limit_value"
```

Ce bloc est tres utile a commenter. Il montre que la requete SQL n'est pas concatenee naivement avec des valeurs libres. Les parametres sont encapsules, la limite est bornee, et les colonnes sont resolues depuis le schema connu. En soutenance, cela me permet de parler a la fois de securite, de maitrise des couts et de gouvernance des acces.

Autrement dit, FastAPI est ici un vrai contrat de service entre le stockage analytique et les consommateurs.

---

## 7. Consommation API cote dashboard - 1 min 30

Le dashboard Streamlit ne va pas directement chercher des fichiers ou des requetes SQL. Il passe par un client applicatif qui encapsule les appels a l'API. Cela permet de garder une architecture propre : le front se concentre sur l'affichage, et la logique d'acces aux donnees reste centralisee.

### Bloc de code 7 - Client de consommation FastAPI pour le front

Source : front-streamlit/dashboard/data_api_client.py

```python
def query_table(
    self,
    table_name: str,
    *,
    filters: list[dict[str, Any]] | None = None,
    limit: int | None = None,
    layer: str = DEFAULT_LAYER,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "limit": limit or self.per_call_limit,
        "layer": layer,
    }
    if filters:
        params["filters"] = json.dumps(filters, ensure_ascii=False)

    return self._safe_get_json(f"/tables/{table_name}", params=params)
```

Ce code montre que le front travaille avec un point d'entree stable. Cela facilite les evolutions, les tests et les changements de structure cote backend. Devant le jury, je peux insister sur l'idee suivante : le front n'est pas branche en direct sur l'entrepot. Il consomme un service propre, ce qui est beaucoup plus defendable en architecture.

---

## 8. Prediction et apprentissage automatique - 2 min 30

La partie predictive vient prolonger le projet vers un usage plus avance. Je la presente comme une brique de valorisation, pas comme une promesse exageree. Le but ici est de montrer qu'a partir des tables gold, nous pouvons entrainer un premier modele exploitable pour estimer la consommation.

Le choix du modele est volontairement sobre. Nous utilisons une regression lineaire comme baseline. C'est un choix defendable en soutenance, parce qu'il permet de montrer un pipeline complet d'entrainement, de pretraitement, d'evaluation et de journalisation, sans sur-promettre une sophistication qui ne serait pas justifiee.

### Bloc de code 8 - Creation du modele et pretraitement

Source : predict/src/predict/model.py et predict/src/predict/preproc.py

```python
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

Ce bloc me permet d'expliquer deux choses. D'abord, le modele lui-meme. Ensuite, la pipeline de pretraitement. Dans le projet, ce pretraitement repose sur une imputation KNN et une standardisation des variables numeriques. Le message a faire passer est qu'on ne jette pas des donnees brutes dans un modele : on prepare un pipeline reproductible.

### Bloc de code 9 - Entrainement et evaluation

Source : predict/src/predict/train.py

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

Quand je commente ce deuxieme extrait, j'explique que la prediction est integree dans une logique data engineer serieuse : chargement depuis BigQuery, separation train test, pretraitement, apprentissage, evaluation, puis reutilisation dans l'API via les endpoints de prediction nationale et regionale.

Ce point est important car il montre que la brique machine learning est connectee au reste du systeme, et non posee artificiellement a cote.

---

## 9. Infrastructure Terraform et industrialisation - 1 min 30

Le dernier pilier du projet est l'infrastructure as code. Cette partie compte beaucoup dans une soutenance data engineer, parce qu'elle montre que le projet a ete pense pour etre deployable et reproductible.

### Bloc de code 10 - Provisioning GCP avec Terraform

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

Ce que je dis ici, c'est que nous ne dependons pas d'une configuration manuelle floue. Le projet GCP, les services, le bucket, les comptes de service et les permissions sont decrits comme du code. C'est une preuve d'industrialisation, mais aussi de reproductibilite.

Cela me permet d'insister sur un point simple : le projet ne vit pas seulement dans un poste local, il est pense comme une solution deployable.

---

## 10. Qualite, limites et conclusion - 1 min 30

Pour terminer, je rappelle que le projet contient egalement des tests unitaires sur plusieurs briques critiques, notamment l'ingestion, certains DAGs et le service BigQuery expose par l'API. Cela renforce la credibilite de l'ensemble, car nous avons cherche a fiabiliser les composants les plus sensibles.

Je peux aussi reconnaitre lucidement les limites actuelles. La brique predictive est encore une baseline et peut etre enrichie. Le front peut encore gagner en profondeur fonctionnelle. Les controles de qualite de donnees peuvent etre renforces. Mais justement, cette lucidite est utile devant un jury : elle montre que nous savons distinguer ce qui est deja livre de ce qui releve de la feuille de route.

Ma conclusion est la suivante : Mix Energy est un projet data de bout en bout, lisible metier, solide techniquement, et suffisamment industrialise pour etre defendu comme un vrai pipeline de production. Nous partons de sources ouvertes, nous les orchestrons, nous les transformons, nous les exposons, nous les visualisons, et nous ouvrons deja vers la prediction. C'est cette coherence globale qui fait la valeur du projet.

Je vous remercie pour votre attention, et je suis disponible pour vos questions.

---

## Questions probables du jury

### Pourquoi avoir choisi FastAPI entre BigQuery et Streamlit ?

Parce que cela decouple la restitution du stockage, centralise les controles d'entree, simplifie la securisation et rend les donnees reutilisables par d'autres consommateurs qu'un seul front.

### Pourquoi dbt dans ce projet ?

Parce que dbt permet de versionner les transformations SQL, de structurer les couches analytiques, de rendre les dependances explicites et de produire des tables orientees usage metier.

### Pourquoi une regression lineaire plutot qu'un modele plus complexe ?

Parce que l'objectif etait d'avoir une baseline robuste et explicable, connectee a un pipeline complet de preparation, d'entrainement et d'exposition. Le choix est raisonnable pour une premiere version defendable.

### Quelle est la principale force du projet ?

Sa coherence de bout en bout. On peut suivre tout le cycle de vie de la donnee depuis la source externe jusqu'au dashboard et a la prediction.

### Quelle serait la suite logique ?

Renforcer les controles de qualite, enrichir les features meteo et environnementales, comparer plusieurs modeles de prediction, et pousser encore plus loin l'automatisation du deploiement.