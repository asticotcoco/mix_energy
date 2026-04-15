# Rapport technique RNCP37827BC01 - Version personnalisee

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

Ce document ecrit a pour objectif de presenter de facon detaillee le projet Mix Energy dans le cadre de la certification RNCP37827BC01. Il est concu pour etre analyse par le jury avant la soutenance. Il met en evidence le travail de fond realise sur le projet, en explicitant les choix techniques, l'architecture, la chaine de traitement des donnees, les composants developpes, les mecanismes de qualite logicielle, ainsi que des extraits de code significatifs issus du depot.

L'ambition du projet est de construire une chaine de valeur complete autour des donnees energetiques francaises : recuperer des donnees heterogenes, les centraliser dans un environnement cloud, les transformer en jeux de donnees exploitables, produire des indicateurs metiers, entrainer des modeles de prediction, exposer le resultat via une API et proposer une visualisation dans un tableau de bord.

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

### 5.1 Sources et formats de donnees

L'ingestion du projet repose sur plusieurs familles de sources. La premiere correspond aux jeux Eco2mix exposes par le portail ODRE, utilises pour recuperer les donnees nationales et regionales de production et de consommation electrique. La seconde correspond a la Base Carbone ADEME, mobilisee comme referentiel de facteurs d'emission. Cette combinaison est importante car elle permet a la fois de suivre les volumes energetiques et de produire des indicateurs carbone directement exploitables.

Les formats manipules ne sont pas homogenes, ce qui justifie un traitement specifique selon le type de source. Cote Eco2mix, le module d'ingestion sait recuperer des exports CSV complets via le endpoint exports/csv, mais aussi des jeux d'enregistrements structures en JSON via le endpoint records. Cote Base Carbone, le fichier est telecharge sous forme de CSV, charge dans pandas avec un separateur point-virgule et un encodage cp1252, puis nettoye avant chargement vers le bucket GCP.

Exemples de formats reellement traites dans le depot :

- export CSV complet d'un dataset Eco2mix pour historiser un jeu de donnees brut ;
- reponse JSON issue d'une requete filtree sur les enregistrements d'un dataset ;
- CSV Base Carbone converti en DataFrame puis normalise avant sauvegarde.

### 5.2 Gestion des erreurs et limitations des APIs

Le code d'ingestion ne suppose pas un acces ideal aux sources. La fonction de bas niveau chargee d'executer les requetes HTTP centralise la gestion des codes de retour et journalise les situations anormales. Les cas 400, 401, 429 et 500 sont traites explicitement, ce qui montre une approche defensive et operationnelle du pipeline.

Le cas du code 429 est particulierement important dans ce projet, car les APIs ouvertes imposees par ODRE sont soumises a des quotas d'utilisation. En cas de depassement, le module lit la charge utile de la reponse, journalise les informations de limitation disponibles comme errorcode, call_limit et limit_time_unit, puis retourne une structure vide afin d'eviter de propager un resultat incoherent dans le reste de la chaine. Cette logique permet de proteger les etapes aval tout en rendant le diagnostic plus simple dans les logs.

Une verification complementaire porte sur le type de contenu retourne. Lors de la recuperation des CSV, le code controle la presence d'un content-type compatible avec text/csv. Lors d'une selection par enregistrements, il verifie la presence d'une reponse JSON. Ce controle evite de poursuivre le traitement avec un format inattendu, par exemple en cas d'erreur applicative cote fournisseur.

### 5.3 Exemples de flux d'ingestion

Le premier flux d'ingestion correspond au telechargement d'un export CSV complet depuis Eco2mix. Le script parcourt une liste de datasets comme eco2mix-national-tr ou eco2mix-regional-cons-def, appelle la fonction retrieve_csv, puis transfere le contenu recupere dans un bucket Google Cloud Storage. Ce flux sert principalement a constituer une base brute historisable, reutilisable ensuite par les etapes de chargement et de transformation.

Un deuxieme flux consiste a ne recuperer qu'un sous-ensemble de donnees via l'endpoint records. La fonction select_data_from_dataset permet de preciser des champs et une clause where, puis retourne une structure JSON contenant les resultats. Dans le script principal, ces resultats sont convertis en DataFrame pandas avant d'etre serialises en CSV et envoyes dans le bucket. Ce mecanisme est utile pour des usages cibles, des controles ponctuels ou des extractions limitees.

Enfin, l'ingestion de la Base Carbone suit un flux specifique. Le fichier distant est telecharge via requests, charge dans pandas, filtre pour ne conserver que les lignes et colonnes utiles au projet, puis converti dans un format propre avant upload. Ce troisieme exemple montre que l'ingestion ne se limite pas a un simple telechargement de fichiers : elle inclut egalement une phase de normalisation metier indispensable pour rendre les donnees exploitables dans les traitements analytiques suivants.

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

### 6.1 Logique des DAGs

L'orchestration Airflow du projet repose sur des DAGs courts, specialises et lisibles. Chaque DAG correspond a un flux metier bien identifie : ingestion Eco2mix nationale temps reel, ingestion regionale, chargement de la Base Carbone ou entrainement des modeles. Cette separation evite de concentrer toute la logique dans un seul pipeline monolithique et facilite a la fois le debogage, la maintenance et l'evolution du systeme.

Sur le plan technique, les DAGs suivent une structure recurrente. Une premiere tache valide l'acces a une ressource critique, par exemple le bucket GCS ou BigQuery. Une deuxieme tache execute l'operation principale, comme la recuperation d'un CSV ou la verification de la presence des tables gold. Une troisieme tache effectue le transfert ou le traitement aval, par exemple le chargement vers BigQuery ou le lancement d'un modele. Cette logique se voit clairement dans le DAG dag_eco2mix_national_tr, qui enchaine controle d'acces au bucket, ingestion du CSV, transfert vers BigQuery puis execution de commandes dbt.

Cette organisation montre un travail de conception plus mature qu'un simple script planifie. Airflow n'est pas utilise ici uniquement comme declencheur horaire, mais comme cadre d'execution permettant de separer les responsabilites, de materialiser les etapes du pipeline et de rendre explicite l'ordre des operations.

### 6.2 Planification et dependances

La planification des DAGs n'est pas uniforme, car elle s'adapte a la nature des donnees traitees. Le DAG dag_eco2mix_national_tr utilise par exemple un MultipleCronTriggerTimetable avec plusieurs expressions cron afin d'augmenter la frequence des rafraichissements pendant les plages horaires utiles en semaine. Cette approche est pertinente pour des donnees temps reel ou quasi temps reel, pour lesquelles une actualisation infra-journaliere apporte une valeur metier directe dans les tables de restitution et le tableau de bord.

Le DAG dag_base_carbone suit au contraire une planification beaucoup plus simple, de type mensuel ou periodique. Ce choix est coherent avec la nature de la source, qui joue ici le role de referentiel et n'a pas besoin d'etre rechargee avec la meme frequence que les jeux Eco2mix. Le projet montre donc une capacite a ajuster l'orchestration au cycle de vie reel des donnees plutot qu'a imposer une frequence unique a tous les pipelines.

Les dependances entre taches sont exprimees explicitement avec les operateurs de chainage Airflow. Dans le DAG d'ingestion nationale, l'ordre check_bucket_connection >> ingest_csv_to_bucket >> transfer_csv_from_bucket_to_bigquery >> dbt_eco2mix_national_tr formalise une regle importante : on ne transforme pas ce qui n'a pas encore ete recupere et charge. Cette explicitation des dependances rend le pipeline plus robuste et plus lisible pour un tiers, notamment dans une logique de reprise sur incident ou d'analyse des echecs.

### 6.3 Entrainement des modeles via Airflow

Le DAG dag_train_model illustre l'extension de l'orchestration au volet machine learning. Il ne se limite pas a lancer un script Python de facon opaque : il commence par verifier la disponibilite des tables gold necessaires a l'entrainement, en particulier nat_tr_predi et reg_tr_predi dans BigQuery. Ce controle prealable est essentiel, car il garantit que l'apprentissage s'appuie sur des donnees preparees en amont par la chaine analytique.

Une fois cette verification effectuee, deux taches distinctes declenchent l'entrainement des modeles national et regional. Le code recupere un client BigQuery a partir du hook Airflow, puis appelle la fonction train du module predict. Le fait de separer ces entrainements en taches dediees rend le flux plus explicite et permet d'identifier plus facilement un echec sur une branche particuliere du pipeline ML.

Ce DAG montre enfin que le projet ne traite pas Airflow comme un simple ordonnanceur ETL. L'orchestrateur sert aussi a synchroniser les etapes data engineering et machine learning. Cette articulation est importante dans un projet professionnalisant, car elle demontre la capacite a piloter un cycle complet allant de la preparation des donnees jusqu'a la production d'artefacts predictifs reutilisables.

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

### 7.1 Modeles Silver

La couche silver joue un role de normalisation et de fiabilisation des donnees sources avant leur exploitation analytique. Dans le projet, les modeles comme eco2mix_national_cons_def_histo.sql et eco2mix_regional_cons_def_histo.sql reprennent les colonnes utiles des sources brutes, leur donnent une structure stable et appliquent les premiers traitements de typage. Cette etape est importante, car elle permet de disposer d'une base coherente avant toute logique d'agregation ou de calcul metier.

Le choix d'une materialisation incremental avec une cle unique sur la date montre une vraie attention a l'industrialisation. Le modele ne recharge pas l'historique complet a chaque execution, mais ne prend en compte que les nouvelles donnees au-dela de la date maximale deja presente dans la table cible. Cette approche limite le cout de traitement et s'aligne avec un fonctionnement de pipeline recurrent en production.

Le modele regional illustre aussi le travail de mise en qualite. Plusieurs colonnes techniques, comme les variables tco_* et tch_*, sont converties avec SAFE_CAST vers FLOAT64 afin de rendre leur exploitation plus robuste dans BigQuery. Cette phase silver ne se contente donc pas de recopier les donnees : elle les rend plus propres, plus typables et plus reutilisables.

### 7.2 Modeles Gold

La couche gold correspond a la production de tables orientees usage metier. Dans le projet, des modeles comme nat_cons_agre_j.sql ou kpi.sql construisent des indicateurs consolides a partir des donnees prealablement nettoyees. On ne se situe plus ici dans une logique de stockage brut, mais dans une logique de restitution, de pilotage et de preparation des usages analytiques.

Le modele nat_cons_agre_j.sql montre bien cette logique. Il agrege les donnees a la journee, extrait les dimensions calendaires utiles comme l'annee, le mois et le jour, puis calcule des volumes interpretable metier comme la production, la consommation ou les previsions. Les coefficients appliques, par exemple 0.5 ou 0.25, traduisent une prise en compte de la granularite temporelle des donnees sources et montrent une vraie comprehension du sens des mesures manipulees.

Le modele kpi.sql constitue une deuxieme illustration forte de la couche gold. Il transforme les agrégats techniques en indicateurs directement lisibles par un utilisateur final, comme la part du nucleaire, la part du thermique, la part des renouvelables ou le taux de CO2 moyen. Cette couche constitue donc le point de jonction entre la transformation SQL et la valeur metier attendue dans le dashboard et l'API.

### 7.3 Feature engineering

Le projet utilise egalement dbt comme brique de preparation pour le machine learning. Le modele reg_tr_predi.sql ne vise pas uniquement a restituer un jeu consolide, mais a produire des variables explicatives directement exploitables par les algorithmes d'apprentissage. Cette demarche est importante, car elle montre que la transformation analytique et la preparation ML sont pensees comme une seule chaine coherente.

Dans ce modele, plusieurs fenetres analytiques sont utilisees pour calculer des moyennes glissantes sur differents horizons temporels. Une moyenne historique globale jusqu'a t-1 est calculee, ainsi qu'une moyenne sur les quatre valeurs precedentes, soit environ une heure, et une moyenne sur une fenetre longue correspondant a trente jours. Ces variables permettent d'introduire de la memoire temporelle dans les donnees sans externaliser cette logique dans un script Python separe.

Le modele enrichit aussi les observations avec des variables calendaires comme l'annee, le mois, le jour, l'heure et la minute. Enfin, il filtre les donnees pour ne conserver que les lignes exploitables avant les valeurs de consommation nulles. Cette approche prouve une capacite a utiliser SQL non seulement pour agreger, mais aussi pour preparer un dataset d'apprentissage structuré, reproductible et directement raccorde au pipeline de prediction.

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

L'architecture de l'API repose sur une separation nette entre la couche web et la couche d'acces aux donnees. Le fichier main.py declare les routes FastAPI, parse les parametres HTTP et convertit les exceptions techniques en reponses HTTP lisibles. La logique de dialogue avec BigQuery est quant a elle centralisee dans BigQueryDatasetService, ce qui rend le service plus testable et plus maintenable. Cette separation est un bon indicateur de maturite, car elle evite de melanger dans les endpoints la validation des entrees, la construction SQL et les details de connexion au backend analytique.

Le chargement de configuration est egalement traite proprement. Le module config.py lit l'environnement, determine le projet GCP, le dataset cible suffixe par _gold, le chemin des credentials et les limites par defaut de l'API. Il gere aussi les origines CORS autorisees pour permettre au front Streamlit d'interroger le service. Cette partie montre que l'API est pensee pour fonctionner dans plusieurs contextes d'execution, tout en conservant une configuration centralisee et explicite.

L'initialisation du service au demarrage de l'application est un autre point fort. Dans create_app, le hook startup charge les settings puis instancie BigQueryDatasetService.create(settings). Ce mecanisme permet de preparer la connexion BigQuery une seule fois et de la rendre disponible via app.state.service. La dependance get_service expose ensuite cette instance aux endpoints tout en renvoyant une erreur 503 si le service n'est pas pret. Cette approche est preferable a une creation ad hoc d'un client BigQuery a chaque requete.

Le projet montre aussi une vraie attention a la validation des entrees. Les filtres recus via l'URL sont d'abord parses comme JSON, puis convertis en objets FilterClause definis avec Pydantic. Le type FilterOperator borne explicitement les operateurs autorises a des valeurs comme eq, gte, contains, in, is_null ou not_null. En complement, le schema impose des champs obligatoires et interdit les attributs inattendus avec extra="forbid". Cette combinaison limite les erreurs de format et renforce la previsibilite de l'API pour le client.

La partie la plus significative se situe dans la construction des requetes BigQuery. Le service ne concatene pas directement les valeurs utilisateurs dans le SQL. Il commence par verifier que la table demandee existe bien dans le dataset, puis que les colonnes demandees appartiennent au schema connu. Pour chaque filtre, il construit une clause SQL sure et des query parameters associes. Les operateurs simples comme eq ou gte utilisent des ScalarQueryParameter, tandis que l'operateur in s'appuie sur ArrayQueryParameter et que contains passe par un LIKE parametre. Cette logique est importante, car elle combine flexibilite fonctionnelle et maitrise du risque d'injection ou d'erreur de typage.

Le service ajoute aussi une couche de robustesse metier avec la gestion des types BigQuery. Les valeurs de filtres sont converties en fonction du type de la colonne cible : entier, flottant, booléen, date, datetime, timestamp ou numeric. Enfin, la limite de lignes n'est jamais laissee librement au client : si elle n'est pas fournie, la valeur par defaut est appliquee, sinon elle est bornee par max_limit avant d'etre injectee comme parametre SQL. Au final, l'API expose donc une interface simple pour le front, mais s'appuie en interne sur une implementation rigoureuse en termes de validation, de securisation et de gestion des erreurs.

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

Cette brique n'est pas un simple script de demonstration. Le code montre une chaine ML complete, depuis l'extraction des donnees de travail dans BigQuery jusqu'a la production d'une prediction exploitable. Le module train.py orchestre ce cycle en chargeant les donnees depuis les tables gold, en construisant les jeux d'entrainement et de test, puis en appelant les differentes etapes du moteur de prediction. La separation entre chargement, pretraitement, apprentissage, evaluation et inference rend l'ensemble plus lisible et plus facilement industrialisable.

La source des donnees d'apprentissage est clairement identifiee dans data.py. Les requetes SQL ciblent les tables nat_tr_predi et reg_tr_predi produites en amont par dbt, ce qui montre une articulation nette entre la couche analytique et la couche machine learning. Le module sait charger soit l'historique complet pour l'entrainement, soit un sous-ensemble recent pour preparer une prediction. Cette organisation est importante, car elle evite de dupliquer la logique de preparation des variables entre SQL et Python.

Le pretraitement est pris en charge par une pipeline scikit-learn declaree dans preproc.py. Cette pipeline combine un KNNImputer pour traiter les valeurs manquantes et un StandardScaler pour normaliser les variables numeriques. Le choix d'un ColumnTransformer permet de selectionner automatiquement les colonnes numeriques et de produire un DataFrame pretraite coherent avec les attentes du modele. Dans model.py, ce preprocesseur est ajuste sur les donnees d'entrainement puis sauvegarde comme artefact distinct, avant d'etre recharge pour transformer les donnees de test ou de prediction. Cette separation entre preprocesseur et modele est une bonne pratique, car elle garantit la coherence entre apprentissage et inference.

Le modele retenu est une regression lineaire de scikit-learn, encapsulee dans la classe Energypredict. La methode create_model instancie LinearRegression puis journalise ses hyperparametres. L'entrainement est ensuite effectue par train_model, qui ajuste le modele sur les donnees pretraitees et l'enregistre sous le nom energy_pred. Ce choix de modele reste simple, mais il est pertinent dans un projet pedagogique et professionnalisant, car il permet d'obtenir une baseline interpretable tout en mettant l'accent sur la structuration du pipeline global.

L'evaluation est egalement explicite dans le code. La methode evaluate_model calcule quatre metriques complementaires : MAE, MSE, R2 et MAPE. Ce choix est interessant, car il permet de croiser une lecture absolue de l'erreur, une penalisation quadratique des ecarts, un indicateur de qualite globale d'ajustement et une mesure relative en pourcentage. Les resultats sont journalises via l'objet MlFlowLogger, ce qui donne au projet une dimension de suivi d'experimentation au-dela d'un simple affichage console.

La journalisation ML est en effet un point fort de cette brique. Le module mllogs.py configure Mlflow, ouvre un run, associe les executions a une experience mensuelle et enregistre a la fois les hyperparametres, les metriques et les artefacts de modele. Le preprocesseur et le modele sont chacun sauvegardes avec un nom versionnable, puis rechargeables via Mlflow lors de l'inference. Cette approche montre que le projet ne se limite pas a entrainer un modele une fois, mais qu'il prepare aussi sa reutilisation et sa tracabilite dans le temps.

Enfin, la prediction en elle-meme est pensee comme un flux distinct de l'entrainement. Les fonctions build_input_national et build_input_region construisent une observation a predire a partir du contexte temporel courant, des consommations recentes et de variables derivees comme prev_conso_mean, prev_conso_mean_h ou prev_conso_mean_m. Le systeme recharge ensuite le preprocesseur et le modele enregistres avant de produire une estimation de consommation. Cet enchainement montre que le projet couvre l'ensemble du cycle ML utile en production : preparation des features, apprentissage, evaluation, stockage des artefacts et inference sur de nouvelles donnees.

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

Les tests ne sont pas limites a des cas superficiels. Ils couvrent plusieurs couches de l'architecture et verifient aussi bien des comportements fonctionnels que des cas d'erreur ou des choix d'implementation. Cette largeur de couverture est importante dans un projet de type data platform, car elle permet de fiabiliser des composants heterogenes : appels HTTP, construction de requetes SQL, chargement BigQuery et orchestration Airflow.

Le sous-projet FastAPI contient par exemple des tests unitaires sur le service d'acces BigQuery. Le fichier test_bigquery_service.py verifie que les tables masquées ne sont pas exposees par defaut, que les colonnes d'une table sont correctement restituees et surtout que les requetes sont construites de facon sure. Un test controle explicitement la presence de parametres nommes comme @filter_0, @filter_1 et @limit_value dans la requete SQL generee, ce qui constitue une preuve concrete de protection contre une construction naive des filtres.

Le module d'ingestion est egalement teste sur des scenarios nominaux et non nominaux. Dans test_eco2mix_ingest.py, des reponses HTTP factices sont injectees pour simuler un succes CSV, un content-type inattendu ou encore un depassement de quota avec code 429. Ce choix est pertinent, car il permet de tester la logique defensive de l'ingestion sans dependre d'un acces reel a l'API ODRE. Le comportement attendu, comme le retour d'un dictionnaire vide en cas de rate limiting, est ainsi verifie de maniere deterministe.

La partie chargement vers BigQuery fait elle aussi l'objet de tests cibles. Le fichier test_bigquery_loader.py verifie que les fichiers sont charges avec la bonne table cible, le bon delimiteur et la bonne politique d'ecriture. Un test montre egalement qu'en cas d'echec de chargement avec le schema initial, le systeme retente avec un schema converti en STRING. Cette strategie est interessante, car elle traduit une logique de resilence face a des variations de format ou de typage dans les fichiers sources.

Enfin, les DAGs Airflow eux-memes sont testes. Le fichier test_dag_eco2mix_national_tr.py n'execute pas un environnement Airflow complet, mais installe des stubs permettant de verifier la structure du DAG, ses tags, ses taches declarees et ses expressions cron. Ce point est important, car il montre que la qualite logicielle porte aussi sur l'orchestration et pas uniquement sur les modules Python classiques. Le projet valide ainsi non seulement le code de traitement, mais aussi la forme attendue des pipelines qui pilotent la chaine globale.

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

## 16. Conclusion

Le projet Mix Energy constitue une preuve solide de travail de fond pour une evaluation par jury avant soutenance. Il couvre un spectre technique large et coherent : ingestion, orchestration, transformation analytique, API, visualisation, prediction et infrastructure cloud.

L'interet principal du projet est sa dimension complete. Il ne s'agit pas d'une demonstration isolee, mais d'une architecture multi-composants reliee par un objectif metier clair. Les fichiers du depot montrent un travail structure, testable, documente par le code et appuye sur des technologies reconnues du monde professionnel.

Pour une certification RNCP37827BC01, ce dossier permet donc de mettre en avant une demarche de conception, de realisation et d'industrialisation logicielle avec une vraie profondeur technique.

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
