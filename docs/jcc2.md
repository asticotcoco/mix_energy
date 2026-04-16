		ARTEFACT SCHOOL OF DATA
Data Engineer RNCP37827 Bloc 1
Rapport de Projet Data Engineering
			Mix énergie et empreinte carbone 
Pipeline ELT avec Documentation du Code 
https://github.com/ThibaultMer/mix_energy/tree/Terra_temp
Equipe: Thibault MERVILLE, Xavier FILAIRE, Kuang ZHENG, Candide HOUNSOU, Jean-Christophe CHARBONNEL
Auteur : Jean-Christophe CHARBONNEL
Période: 30 mars 2026 – 13 avril 2026

Session Data Engineering – School Of Data Artefact – Mars. Avril. 2026
Table des matières
Introduction ........................................................................................................ 4
________________________________________
1. Cadrage métier et vision du projet .................................................................... 4
1.1 Intitulé du projet ............................................................................................ 4
1.2 Présentation générale .................................................................................... 4
1.3 Objectifs métier ............................................................................................. 5
1.4 Justification du choix du sujet ........................................................................ 6
1.5 Sources de données mobilisées ou ciblées ..................................................... 6
1.6 Architecture fonctionnelle cible ..................................................................... 7
1.7 Exemple d’appel API ...................................................................................... 7
1.8 Architecture technique cible et couverture RNCP ........................................... 8
________________________________________
2. Contexte et problématique .............................................................................. 9
2.1 Présentation générale de la solution ............................................................. 10
________________________________________
3. Architecture technique .................................................................................. 11
3.1 Couche d’ingestion et d’orchestration .......................................................... 12
3.2 Couche de stockage et de transformation ..................................................... 13
3.3 Couche d’exposition .................................................................................... 14
3.4 Couche de présentation ............................................................................... 15
3.5 Couche infrastructure et déploiement .......................................................... 16
________________________________________
4. Flux de données de bout en bout .................................................................... 17
________________________________________
5. Ingestion des données ................................................................................... 18
5.1 Sources et formats de données .................................................................... 19
5.2 Gestion des erreurs et limitations des APIs ................................................... 20
5.3 Exemples de flux d’ingestion ........................................................................ 20
________________________________________


6. Orchestration des traitements (Airflow) .......................................................... 22
6.1 Logique des DAGs ........................................................................................ 23
6.2 Planification et dépendances ....................................................................... 23
6.3 Entraînement des modèles via Airflow .......................................................... 24
________________________________________
7. Transformations analytiques (dbt) .................................................................. 26
7.1 Modèles Silver ............................................................................................. 26
7.2 Modèles Gold .............................................................................................. 27
7.3 Feature engineering ..................................................................................... 28
________________________________________
8. Exposition des données via API (FastAPI) ........................................................ 31
________________________________________
9. Frontend et restitution (Streamlit) .................................................................. 35
________________________________________
10. Prédiction et machine learning ..................................................................... 36
________________________________________
11. Infrastructure as Code et industrialisation .................................................... 39
________________________________________
12. Qualité logicielle et tests .............................................................................. 41
________________________________________
13. Compétences mobilisées et en adéquation RNCP ......................................... 44
________________________________________
14. Difficultés techniques .................................................................................. 44
________________________________________
15. Résultats et valeur produite .......................................................................... 45
________________________________________
16. Conclusion .................................................................................................. 45
________________________________________
17. Annexes ....................................................................................................... 46






Introduction
L'objectif du projet est de construire et de mettre à disposition pour le client un data pipeline, appelé aussi chaine de valeur complète autour des données énergétiques françaises : récupérer des données hétérogènes, les centraliser dans un environnement cloud, les transformer en jeux de données exploitables, produire des indicateurs métiers, entrainer des modèles de prédiction, exposer le résultat via une API et proposer une visualisation dans un tableau de bord. Ce data-pipeline repose sur une architecture générée et déployée de manière automatisée sans écrire de lignes de code pour créer cette architecture avec les ressources nécessaires modifiables en temps réel sur un ou plusieurs environnements « clouds » proposés par les éditeurs logiciels. L’affichage de prédictions sur ce tableau de bord ajoute de la valeur ajoutée métier pour anticiper les pics de production à venir en cas de forte chaleur ou de période hivernale très froide par exemple.

1. Cadrage métier et vision ciblée du projet
Mix Energie et empreinte carbone 
Construction d’un data-pipeline bâti sur la collecte, la transformation, l’exposition et la valorisation de données énergétiques, météo et de qualité de l’air en France.

1.1 Intitule du projet

Projet Energie - Mix électrique français et empreinte carbone

1.2 Présentation générale

Le projet Mix Energy s'inscrit dans une problématique actuelle au croisement de la transition énergétique, de la valorisation des données et de l'aide à la décision. Il vise à concevoir une chaine de traitement de données complète permettant de collecter, structurer, transformer et restituer des informations relatives au mix électrique français et à son empreinte carbone.

L'objectif est double. D'une part, il s'agit de produire des indicateurs fiables et lisibles sur la production électrique par filière de production d’énergie, la consommation d’énergie et la quantité carbone émise dans l’atmosphère terrestre qui est associée à cette production d’énergie. D'autre part, le projet montre qu’il existe une possibilité de prédiction et d'anticipation de la consommation d’énergie en fonction des sources de production disponibles et aussi des conditions météorologiques du moment donné que nous voulons quantifier. En commençant par les seules données de puissance d’énergie électrique produite puis en envisageant un enrichissement par des données météorologiques historiques et prévisionnelles.

Cette partie de définition de périmètre du document formalise le cadrage métier et la vision cible du projet. Elle complète les preuves techniques présentées plus loin dans le rapport et permet de distinguer ce qui relève du socle de l’ensemble de valeurs de production d’énergie déjà implémenté dans le dépôt distant de téléchargement sur les sites internet de RTE, de ce qui constitue une perspective de visualisation ciblée de prédiction de trajectoire d'évolution crédibilisée par des graphiques visuels interactifs, intuitifs et modifiables à volonté de mesures de quantités d’énergie produites mises à jour quotidiennes.

1.3 Objectif métier

L'objectif métier principal consiste à construire un pipeline de données capable d'ingérer des données de production électrique par source, telles que le nucléaire, le solaire, l'éolien, le gaz ou l'hydraulique, puis de calculer l'empreinte carbone du mix électrique français en temps quasi réel, avant de restituer ces informations dans un tableau de bord de suivi national et régional.

A moyen terme, ce socle de données à vocation à supporter un cas d'usage prédictif plus ambitieux. Il s'agit de mettre en place une estimation de la consommation électrique à J+1. Dans une première phase, cette prédiction peut s'appuyer exclusivement sur les variables énergétiques. Dans une seconde phase, elle peut être enrichie par des données météorologiques historiques et prévisionnelles afin d'améliorer la qualité des modelés.

1.4 Justification du choix du sujet

Le choix de ce projet repose sur plusieurs arguments. Il s'agit d'un cas métier immédiatement compréhensible, fortement visuel et directement relié à des enjeux actuels de transition énergétique. Il présente également un intérêt professionnel clair pour des recruteurs et acteurs du secteur Energie, notamment des entreprises telles que Schneider Electric ou EDF R&D ou RTE.

Le projet bénéficie en outre d'un écosystème de sources ouvertes favorable. Les APIs et jeux de données mobilisées sont publiques, documentées, relativement stables et exploitables sans coût d'entrée important d’inscription en ligne web sur les sites où elles sont disponibles. Ce contexte rend la démarche techniquement réaliste dans un cadre pédagogique tout en conservant une forte valeur démonstrative devant un jury.

1.5 Sources de données mobilisées ou ciblées

Le projet s'appuie d'abord sur les jeux de données Eco2mix diffusées via le portail ODRE. Ces données permettent d'accéder aux informations nationales et régionales sur la consommation, la production par filière, les échanges et certaines estimations associées au système électrique. Les ensembles de données eco2mix-national-tr, eco2mix-national-cons-def, eco2mix-regional-tr et eco2mix-regional-cons-def constituent le cœur du dispositif de suivi et d'historisation. Le quota de connexions distantes quotidien annoncé sur ODRE est de 50 000 appels API par utilisateur et par mois, ce qui justifie une orchestration maitrisée des appels.

La Base Carbone ADEME joue un rôle de référentiel métier. Elle apporte les facteurs d'émission de gaz à effet de serre par filière de production électrique et permet, par jointure, de convertir les volumes de production en indicateurs d'empreinte carbone.

Dans la vision cible du projet, l'intégration de données météorologiques constitue une extension naturelle. Des services comme Open-Météo permettent de récupérer à la fois des historiques mis à jour régulièrement et des prévisions de température, vent, précipitations et humidité, utiles pour expliquer et prédire les variations de consommation électrique à venir.

Une autre extension pertinente consiste à intégrer des données de qualité de l'air, par exemple via Atmo Data, afin de rapprocher l'intensité carbone du mix électrique et les indicateurs territoriaux de pollution atmosphérique. Cette extension renforce la portée analytique du projet sans être présentée ici comme entièrement livrée dans le dépôt actuel distant.

Cette extension a depuis été concrètement mise en oeuvre dans le projet. Deux modules d'ingestion Python dédiés ont été ajoutés pour récupérer des données météo par ville et des données de qualité de l'air par ville et par zone ATMO. Les jeux collectés sont historisés, chargés dans BigQuery puis transformés avec dbt dans des tables de travail nommées meteo_by_city et air_quality_by_city. Le périmètre ne se limite donc plus aux seules données énergétiques et carbone : il inclut désormais un enrichissement environnemental exploitable dans l'API et dans le dashboard.

1.6 Architecture fonctionnelle cible

L'architecture fonctionnelle du projet repose sur une logique de pipeline structuré en plusieurs temporalités. Une phase d'initialisation permet de constituer le socle historique à partir des données consolidées nationales et régionales ainsi que du référentiel carbone. Une phase récurrente alimente ensuite les données du jour ou du mois via les jeux temps réel et les traitements correctifs. Enfin, les transformations analytiques permettent de produire des tables orientées usage pour le suivi, le calcul de KPIs et la prédiction.

Dans cette vision cible, un DAG Airflow quotidien ou infra-journalier alimente les données temps réel, tandis qu'un DAG mensuel ou périodique remplace les données provisoires par les versions consolidées lorsqu'elles deviennent disponibles. Les transformations dbt servent ensuite à produire les tables de restitution, les croisements analytiques et les jeux de données prêts pour les usages machine learning.

1.7 Exemple d'appel API

L'accès aux jeux de données ODRE peut être réalise via une requête HTTP paramétrée. L'exemple suivant illustre le principe général d'interrogation des jeux Eco2mix et justifie le choix d'une couche d'ingestion Python légère, reposant sur la librairie du package python « requests ». Ci-dessous un exemple de bloc de code python qui gère l’ingestion de données :

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

1.8 Architecture technique cible et couverture RNCP

Sur le plan technique, le projet repose sur une architecture modulaire articulée autour de plusieurs composants spécialisés : ingestion Python, stockage intermédiaire dans GCP Storage, transformations dbt, stockage analytique dans BigQuery, orchestration Airflow, exposition des données via FastAPI et restitution dans Streamlit. L'infrastructure GCP et le provisioning Terraform donnent à cette chaîne de logiciels combinés ensemble une dimension industrialisable.

Dans la cible d'architecture complète, des briques supplémentaires peuvent renforcer le dispositif, notamment des contrôles de qualité de données formalises, une chaine CI/CD et des enrichissements multi-sources autour de la météo et de la qualité de l'air. Ces composants sont présents comme extensions ou feuille de route lorsque leur implémentation n'est pas intégralement visible dans le dépôt actuel github.

Le projet présente enfin un fort alignement avec les attendus pédagogiques et RNCP. Il couvre l'extraction automatisée de données multi-sources, la structuration et l'homogénéisation des jeux de données, les transformations analytiques SQL, l'orchestration de pipelines, l'exposition de services REST et la restitution visuelle dans un dashboard. Cette articulation renforce la lisibilité du projet pour une interprétation visuelle intuitive et valorise sa cohérence de bout en bout.
 
2. Contexte et problématique

Le secteur de l’énergie est fortement dépendant de la disponibilité de données fiables, régulières et interprétables. Les données de production, de consommation, d'émissions et de contexte exogène comme la météo ou la qualité de l'air doivent être rapprochées pour permettre des analyses utiles et des prédictions court terme.

Le projet Mix Energy répond à plusieurs besoins concrets :

- centraliser des données provenant de plusieurs sources ouvertes ;
- historiser ces données dans un environnement analytique exploitable ;
- construire des tables consolidées orientées usage métier ;
- produire des indicateurs de pilotage, notamment sur le mix énergétique et le CO2 ;
- préparer des données pour la prédiction de consommation ;
- entrainer des modèles de machine learning pour l'anticipation des besoins ;
- exposer les données dans une API fiable et réutilisable ;
- proposer une interface de visualisation orientée lecture et analyse.

Le travail de fond ne se limite donc pas à une application unique. Il couvre l'ensemble du cycle de vie de la donnée, depuis l'ingestion jusqu'à la restitution visuelle, avec une logique de production et de déploiement.

2.1 Présentation générale de la solution

Le dépôt github est organisé en plusieurs briques complémentaires :

- Airflow pour l'orchestration des flux et le déclenchement des traitements ;
- dbt pour la transformation SQL et la structuration des couches analytiques ;
- FastAPI pour l'exposition read-only des données consolidées ;
- Streamlit pour la visualisation et la navigation dans les indicateurs ;
- un module de prédiction en Python pour l'entrainement des modèles ;
- Terraform pour l'infrastructure GCP ;
- des tests unitaires pour valider les composants critiques.

Cette décomposition montre une approche modulaire du projet. Chaque composant a une responsabilité claire, ce qui facilite la maintenance, la lisibilité et la possibilité de faire évoluer le système.

3. Architecture technique

L'architecture technique repose sur une chaine de traitement en couches :

 

3.1 Couche ingestion et orchestration 

Les DAGs Airflow présents dans le dossier airflow/dags pilotent les traitements. Ils assurent notamment :

- la vérification de la disponibilité du bucket de stockage ;
- l'ingestion des fichiers CSV depuis des jeux de données externes ;
- l'ingestion des données météo et qualité de l'air pour plusieurs villes ;
- le transfert des fichiers vers BigQuery ;
- le déclenchement des transformations dbt ;
- l'entrainement des modèles de prédiction.

Les fichiers les plus représentatifs sont :

- airflow/dags/dag_base_carbone.py
- airflow/dags/dag_eco2mix_national_tr.py
- airflow/dags/dag_eco2mix_national_cons_def.py
- airflow/dags/dag_eco2mix_regional_tr.py
- airflow/dags/dag_eco2mix_regional_cons_def.py
- airflow/dags/dag_meteo.py
- airflow/dags/dag_air_quality.py
- airflow/dags/dag_train_model.py

3.2 Couche stockage et transformation 

 
Les données sont chargées dans BigQuery puis transformées via dbt. Le projet dbt distingue au minimum deux couches de travail :
 

- une couche silver pour nettoyer, typer et homogénéiser ;
- une couche gold pour agréger, calculer les indicateurs et préparer les données de prédiction.

Cette séparation est importante. Elle montre un travail de structuration analytique et non un simple empilement de scripts. Une couche bronze

3.3 Couche exposition 
Le service FastAPI fournit une couche d'accès standardisé aux données consolidées. L'API permet de :

- lister les tables disponibles ;
- lister les colonnes d'une table ;
- interroger une table avec des filtres et une limite.

Cette couche sert d'interface entre le stockage analytique et le front. Elle contribue à découpler la présentation des mécanismes internes de stockage.

3.4 Couche présentation
 
Le front end Streamlit propose plusieurs vues :

- historique national ;
- temps réel national ;
- historique régional ;
- temps réel régional.

Le front n'est pas un simple prototype. Le code montre un travail de structuration de pages, de style, et de chargement cible des données via l'API.

3.5 Couche infrastructure et déploiement
 
Le dossier iac contient une infrastructure as code Terraform pour Google Cloud Platform. On y trouve notamment :
 
- la création du projet GCP ;
- l'activation des services cloud ;
- la création de comptes de service dédiés ;
- la création d'un bucket GCS ;
- la mise en place d'Artifact Registry ;
- l'attribution de rôles IAM adaptes.

Cela renforce la dimension professionnelle du projet : le système n'est pas seulement développé localement, il est pensé pour être déployé et administré.

4. Flux de données de bout en bout
 
Le flux principal du projet peut être résumé ainsi :

1. récupération de données externes ;
2. dépôt dans un bucket GCS ;
3. chargement vers BigQuery ;
4. transformation dbt vers des tables analytiques ;
5. exploitation pour les KPIs et la prédiction ;
6. exposition via FastAPI ;
7. consommation via Streamlit.

Ce flux de bout en bout constitue un point fort du projet. Il démontre une capacité à traiter un besoin data complet et pas uniquement une brique isolée.

5. Ingestion des données 
Le module d'ingestion contient une logique réelle de communication avec des sources externes. Le fichier ingest_dbt/src/mix_energy/eco2mix_ingest.py montre par exemple :
- la construction d'URL vers l'API de données ouverte ;
- la gestion explicite des codes HTTP 200, 400, 401, 429 et 500 ;
- la récupération des exports CSV ;
- la sélection d'enregistrements pour certains usages ;
- le chargement ultérieur vers le bucket.

Cette gestion prouve que le travail ne s'est pas limité à un cas idéal. Les erreurs réseau et les statuts de retour sont pris en compte.




5.1 Sources et formats de données

L'ingestion du projet repose sur plusieurs familles de sources. La première correspond aux jeux Eco2mix exposes par le portail ODRE, utilises pour récupérer les données nationales et régionales de production et de consommation électrique. La seconde correspond à la Base Carbone ADEME, mobilisée comme référentiel de facteurs d'émission. Cette combinaison est importante car elle permet à la fois de suivre les volumes énergétiques et de produire des indicateurs carbone directement exploitables.

Les données reçues par requête retour de serveur se présentent par défaut sous la forme de chaîne de caractères json donc formattées au fichier json qui est le format des requêtes http en général pris par défaut, soit sous la forme de fichiers csv au format excel simple avec en séparateur « , » ou « ; » suivant le choix  pris pour le formatage des données reçues.

Les formats manipulés ne sont pas homogènes, ce qui justifie un traitement spécifique selon le type de source. Cote Eco2mix, le module d'ingestion sait récupérer des exports CSV complets via le endpoint exports/csv, mais aussi des jeux d'enregistrements structures en JSON via le endpoint records. Cote Base Carbone, le fichier est téléchargé sous forme de CSV, charge dans pandas avec un séparateur point-virgule et un encodage cp1252, puis nettoyé avant chargement vers le bucket GCP.

Exemples de formats réellement traités dans le dépôt :

- export CSV complet d'un dataset Eco2mix pour historiser un jeu de données brut ;
- réponse JSON issue d'une requête filtrée sur les enregistrements d'un dataset ;
- CSV Base Carbone converti en DataFrame puis normalise avant sauvegarde.




5.2 Gestion des erreurs et limitations des APIs

Le code d'ingestion ne suppose pas un accès idéal aux sources. La fonction de bas niveau chargée d'exécuter les requêtes HTTP centralise la gestion des codes de retour et journalise les situations anormales. Les cas 400, 401, 429 et 500 sont traites explicitement, ce qui montre une approche défensive et opérationnelle du pipeline.

Le cas du code 429 est particulièrement important dans ce projet, car les APIs ouvertes imposées par ODRE sont soumises à des quotas d'utilisation. En cas de dépassement, le module lit la charge utile de la réponse, journalise les informations de limitation disponibles comme errorcode, call_limit et limit_time_unit, puis retourne une structure vide afin d'éviter de propager un résultat incohérent dans le reste de la chaine. Cette logique permet de protéger les étapes aval tout en rendant le diagnostic plus simple dans les logs.

Une vérification complémentaire porte sur le type de contenu retourne. Lors de la récupération des CSV, le code contrôle la présence d'un content-type compatible avec text/csv. Lors d'une sélection par enregistrements, il vérifie la présence d'une réponse JSON. Ce contrôle évite de poursuivre le traitement avec un format inattendu, par exemple en cas d'erreur applicative cote fournisseur.

5.3 Exemples de flux d'ingestion

Le premier flux d'ingestion correspond au téléchargement d'un export CSV complet depuis Eco2mix. Le script parcourt une liste de datasets comme eco2mix-national-tr ou eco2mix-regional-cons-def, appelle la fonction « retrieve_csv », puis transfère le contenu récupère dans un bucket Google Cloud Storage. Ce flux sert principalement à constituer une base brute historisable, réutilisable ensuite par les étapes de chargement et de transformation.

Un deuxième flux consiste à ne récupérer qu'un sous-ensemble de données via l'endpoint records. La fonction « select_data_from_dataset » permet de préciser des champs et une clause « where », puis retourne une structure JSON contenant les résultats. Dans le script principal, ces résultats sont convertis en DataFrame pandas avant d'être sérialisés en CSV et envoyés dans le bucket. Ce mécanisme est utile pour des usages cibles, des contrôles ponctuels ou des extractions limitées.

Enfin, l'ingestion de la Base Carbone suit un flux spécifique. Le fichier distant est téléchargé via le package « requests », charge dans pandas, filtre pour ne conserver que les lignes et colonnes utiles au projet, puis converti dans un format propre avant le chargement « upload ». Ce troisième exemple montre que l'ingestion ne se limite pas à un simple téléchargement de fichiers : elle inclut également une phase de normalisation métier indispensable pour rendre les données exploitables dans les traitements analytiques suivants.

### Extrait de code 1 - Gestion de la réponse HTTP

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

Cet extrait est important parce qu'il montre une logique défensive et une prise en compte des limitations d'API, notamment le taux limite « rate limiting ».


6. Orchestration Airflow
 
Les DAGs structurent le traitement. Ils combinent vérification de connexion, ingestion, transfert vers BigQuery et exécution de commandes dbt. Le code montre aussi des horaires de déclenchement précis, adaptés au type de données.
6.1 Logique des DAGs

L'orchestration Airflow du projet repose sur des DAGs courts, spécialisés et lisibles. Chaque DAG correspond à un flux métier bien identifie : ingestion Eco2mix nationale temps réel, ingestion régionale, chargement de la Base Carbone ou entrainement des modelés. Cette séparation évite de concentrer toute la logique dans un seul pipeline monolithique et facilite à la fois le débogage, la maintenance et l'évolution du système.

Sur le plan technique, les DAGs suivent une structure récurrente. Une première tâche valide l'accès à une ressource critique, par exemple le bucket GCS ou BigQuery. Une deuxième tâche exécute l'opération principale, comme la récupération d'un CSV ou la vérification de la présence des tables gold. Une troisième tâche effectue le transfert ou le traitement aval, par exemple le chargement vers BigQuery ou le lancement d'un modèle. Cette logique se voit clairement dans le DAG dag_eco2mix_national_tr, qui enchaine contrôle d'accès au bucket, ingestion du CSV, transfert vers BigQuery puis exécution de commandes dbt.

Cette organisation montre un travail de conception plus mature qu'un simple script planifie. Airflow n'est pas utilisé ici uniquement comme déclencheur horaire, mais comme cadre d'exécution permettant de séparer les responsabilités, de matérialiser les étapes du pipeline et de rendre explicite l'ordre des opérations.

6.2 Planification et dépendances

La planification des DAGs n'est pas uniforme, car elle s'adapte àla nature des données traitées. Le DAG dag_eco2mix_national_tr utilise par exemple un MultipleCronTriggerTimetable avec plusieurs expressions cron afin d'augmenter la fréquence des rafraichissements pendant les plages horaires utiles en semaine. Cette approche est pertinente pour des données temps réel ou quasi-temps réel, pour lesquelles une actualisation infra-journalière apporte une valeur métier directe dans les tables de restitution et le tableau de bord.

Le DAG dag_base_carbone suit au contraire une planification beaucoup plus simple, de type mensuel ou périodique. Ce choix est cohérent avec la nature de la source, qui joue ici le rôle de référentiel et n'a pas besoin d'être rechargée avec la même fréquence que les jeux Eco2mix. Le projet montre donc une capacite à ajuster l'orchestration au cycle de vie réel des données plutôt qu'à imposer une fréquence unique à tous les pipelines.

Les dépendances entre tâches sont exprimées explicitement avec les opérateurs de chainage Airflow. Dans le DAG d'ingestion nationale, l'ordre check_bucket_connection >> ingest_csv_to_bucket >> transfer_csv_from_bucket_to_bigquery >> dbt_eco2mix_national_tr formalise une règle importante : on ne transforme pas ce qui n'a pas encore été récupéré et charge. Cette explicitation des dépendances rend le pipeline plus robuste et plus lisible pour un tiers, notamment dans une logique de reprise sur incident ou d'analyse des échecs.

6.3 Entrainement des modèles via Airflow

Le DAG dag_train_model illustre l'extension de l'orchestration au volet machine learning. Il ne se limite pas à lancer un script Python de façon opaque : il commence par vérifier la disponibilité des tables gold nécessaires l'entrainement, en particulier nat_tr_predi et reg_tr_predi dans BigQuery. Ce contrôle préalable est essentiel, car il garantit que l'apprentissage s'appuie sur des données préparées en amont par la chaine analytique.

Une fois cette vérification effectuée, deux tâches distinctes déclenchent l'entrainement des modèles national et régional. Le code récupère un client BigQuery à partir du hook Airflow, puis appelle la fonction train du module predict. Le fait de séparer ces entrainements en tâches dédiées rend le flux plus explicite et permet d'identifier plus facilement un échec sur une branche particulière du pipeline ML.

Ce DAG montre enfin que le projet ne traite pas Airflow comme un simple ordonnanceur ETL. L'orchestrateur sert aussi à synchroniser les étapes data engineering et machine learning. Cette articulation est importante dans un projet professionnalisant, car elle démontre la capacite à piloter un cycle complet allant de la préparation des données jusqu'à la production d'artefacts prédictifs réutilisables.


### Extrait de code 2 - Entrainement des modèles via Airflow

```python
@dag(
    dag_id="dag_train_model",
    description="Entraine les modèles de machine learning pour la prédiction de consommation d’énergie.",
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

Cet extrait montre plusieurs éléments de fond :

- l'usage d'une orchestration formelle ;
- une planification non triviale ;
- la vérification préalable de la disponibilité des ressources ;
- la prise en compte de la couche BigQuery dans le pipeline ML.

7. Transformations analytiques avec dbt
 
L'une des preuves les plus fortes du travail de fond se trouve dans les modèles SQL dbt. Les fichiers du dossier dbt/models/gold montrent que les données ne sont pas seulement stockées mais structurées pour l'analyse et la prédiction.

Le modèle dbt reg_tr_predi.sql prépare par exemple des variables de travail à partir d'historiques de consommation. On y trouve des fenêtres analytiques, des extractions temporelles et des moyennes glissantes.

7.1 Modèles Silver

La couche silver joue un rôle de normalisation et de fiabilisation des données sources avant leur exploitation analytique. Dans le projet, les modèles comme eco2mix_national_cons_def_histo.sql et eco2mix_regional_cons_def_histo.sql reprennent les colonnes utiles des sources brutes, leur donnent une structure stable et appliquent les premiers traitements de typage. Cette étape est importante, car elle permet de disposer d'une base cohérente avant toute logique d'agrégation ou de calcul métier.

Le choix d'une matérialisation incrémentale avec une clé unique sur la date montre une vraie attention à l'industrialisation. Le modèle ne recharge pas l'historique complet à chaque exécution, mais ne prend en compte que les nouvelles données au-delà de la date maximale déjà présente dans la table cible. Cette approche limite le cout de traitement et s'aligne avec un fonctionnement de pipeline récurrent en production.

Le modèle régional illustre aussi le travail de mise en qualité. Plusieurs colonnes techniques, comme les variables tco_* et tch_*, sont converties avec SAFE_CAST vers FLOAT64 afin de rendre leur exploitation plus robuste dans BigQuery. Cette phase silver ne se contente donc pas de recopier les données : elle les rend plus propres, plus typables et plus réutilisables.

Cette logique silver a été étendue aux données environnementales. Le modèle meteo_by_city.sql unifie les sources météo par ville, harmonise la colonne temporelle time et prépare un historique homogène exploitable dans des visualisations fines. Le modèle air_quality_by_city.sql normalise quant à lui les dates de diffusion et d'échéance, typise les coordonnées et les indices de pollution, puis constitue une base détaillée réutilisable soit pour l'analyse quotidienne, soit pour une cartographie par zone.

7.2 Modèles Gold

La couche gold correspond à la production de tables orientées usage métier. Dans le projet, des modèles comme nat_cons_agre_j.sql ou kpi.sql construisent des indicateurs consolides à partir des données préalablement nettoyées. On ne se situe plus ici dans une logique de stockage brut, mais dans une logique de restitution, de pilotage et de préparation des usages analytiques.

Le modèle nat_cons_agre_j.sql montre bien cette logique. Il agrège les données à la journée, extrait les dimensions calendaires utiles comme l'année, le mois et le jour, puis calcule des volumes interprétable métier comme la production, la consommation ou les prévisions. Les coefficients appliques, par exemple 0.5 ou 0.25, traduisent une prise en compte de la granularité temporelle des données sources et montrent une vraie compréhension du sens des mesures manipulées.

Le modèle kpi.sql constitue une deuxième illustration forte de la couche gold. Il transforme les agrégats techniques en indicateurs directement lisibles par un utilisateur final, comme la part du nucléaire, la part du thermique, la part des renouvelables ou le taux de CO2 moyen. Cette couche constitue donc le point de jonction entre la transformation SQL et la valeur métier attendue dans le dashboard et l'API.

Des modèles gold ont également été ajoutés pour les nouvelles données environnementales. gold_meteo_by_city.sql produit une synthèse quotidienne par ville à partir des observations horaires, avec des indicateurs comme les températures moyenne, minimale et maximale, les cumuls de précipitations, la couverture nuageuse moyenne ou la vitesse moyenne du vent. gold_air_quality_by_city.sql produit une synthèse quotidienne de la qualité de l'air par ville en conservant le dernier snapshot par zone avant agrégation, puis expose des métriques comme avg_quality_code, max_quality_code, last_update_at ou worst_quality_label. Cette évolution montre que la couche gold du projet ne sert pas uniquement aux agrégats énergétiques, mais devient aussi un support de lecture métier pour les données environnementales.

7.3 Feature engineering

Le projet utilise également dbt comme brique de préparation pour le machine learning. Le modèle reg_tr_predi.sql ne vise pas uniquement à restituer un jeu consolide, mais à produire des variables explicatives directement exploitables par les algorithmes d'apprentissage. Cette démarche est importante, car elle montre que la transformation analytique et la préparation ML sont pensées comme une seule chaine cohérente.

Dans ce modèle, plusieurs fenêtres analytiques sont utilisées pour calculer des moyennes glissantes sur différents horizons temporels. Une moyenne historique globale jusqu'à t-1 est calculée, ainsi qu'une moyenne sur les quatre valeurs précédentes, soit environ une heure, et une moyenne sur une fenêtre longue correspondant à trente jours. Ces variables permettent d'introduire de la mémoire temporelle dans les données sans externaliser cette logique dans un script Python sépare.

Le modèle enrichit aussi les observations avec des variables calendaires comme l'année, le mois, le jour, l'heure et la minute. Enfin, il filtre les données pour ne conserver que les lignes exploitables avant les valeurs de consommation nulles. Cette approche prouve une capacite à utiliser SQL non seulement pour agréger, mais aussi pour préparer un dataset d'apprentissage structuré, reproductible et directement raccorde au pipeline de prédiction.

Le modèle dbt reg_tr_predi.sql prépare par exemple des variables de travail à partir d'historiques de consommation. On y trouve des fenêtres analytiques, des extractions temporelles et des moyennes glissantes.

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

Cet extrait prouve plusieurs compétences :

- maîtrise des fonctions analytiques SQL ;
- capacité à préparer des variables pertinentes pour le machine learning ;
- structuration d'une chaine de transformation reproductible.

Le modèle kpi.sql montre en outre une logique métier orientée usage.

### Extrait de code 4 - Calcul d'indicateurs métier

```sql
select
SUM(production) AS production_totale,
SUM(nucleaire) / SUM(production) AS pct_nucleaire,
SUM(fioul + charbon + gaz) / SUM(production) AS pct_thermique,
SUM(eolien + solaire + hydraulique + bioenergies) / SUM(production) AS pct_renouvelable,
SUM(taux_co2 * production) / SUM(production) AS taux_co2
from {{ref('nat_cons_agre_j')}}
```

Ce calcul relie directement la technique à une lecture métier du mix énergétique.







8. Exposition des données via FastAPI
 

Le service FastAPI n'est pas uniquement un point d'entrée minimal. Le code montre une API bien structurée, avec :

- un chargement de configuration dédié ;
- une initialisation du service à l'ouverture ;
- des schémas de validation ;
- une gestion propre des erreurs ;
- des filtres dynamiques sur les requêtes.

L'architecture de l'API repose sur une séparation nette entre la couche web et la couche d'accès aux données. Le fichier main.py déclare les routes FastAPI, parse les paramètres HTTP et convertit les exceptions techniques en réponses HTTP lisibles. La logique de dialogue avec BigQuery est quant à elle centralisée dans BigQueryDatasetService, ce qui rend le service plus testable et plus maintenable. Cette séparation est un bon indicateur de maturité, car elle évite de mélanger dans les endpoints la validation des entrées, la construction SQL et les détails de connexion au backend analytique.

Le chargement de configuration est également traité proprement. Le module config.py lit l'environnement, détermine le projet GCP, le dataset cible suffixe par _gold, le chemin des credentials et les limites par défaut de l'API. Il gère aussi les origines CORS autorisées pour permettre au front Streamlit d'interroger le service. Cette partie montre que l'API est pensée pour fonctionner dans plusieurs contextes d'exécution, tout en conservant une configuration centralisée et explicite.

L'initialisation du service au démarrage de l'application est un autre point fort. Dans create_app, le hook startup chargé les settings puis instancie BigQueryDatasetService.create(settings). Ce mécanisme permet de préparer la connexion BigQuery une seule fois et de la rendre disponible via app.state.service. La dépendance get_service expose ensuite cette instance aux endpoints tout en renvoyant une erreur 503 si le service n'est pas prêt. Cette approche est préférable à une création ad hoc d'un client BigQuery à chaque requête.

Le projet montre aussi une vraie attention à la validation des entrées. Les filtres reçus via l'URL sont d'abord parses comme JSON, puis convertis en objets FilterClause definis avec Pydantic. Le type FilterOperator borne explicitement les opérateurs autorises à des valeurs comme eq, gte, contains, in, is_null ou not_null. En complément, le schéma impose des champs obligatoires et interdit les attributs inattendus avec extra="forbid". Cette combinaison limite les erreurs de format et renforce la prévisibilité de l'API pour le client.

La partie la plus significative se situe dans la construction des requêtes BigQuery. Le service ne concatène pas directement les valeurs utilisateurs dans le SQL. Il commence par verifier que la table demandée existe bien dans le dataset, puis que les colonnes demandées appartiennent au schéma connu. Pour chaque filtre, il construit une clause SQL sure et des query parameters associes. Les opérateurs simples comme eq ou gte utilisent des ScalarQueryParameter, tandis que l'opérateur in s'appuie sur ArrayQueryParameter et que contains passe par un LIKE paramètre. Cette logique est importante, car elle combine flexibilité fonctionnelle et maitrise du risque d'injection ou d'erreur de typage.

Le service ajoute aussi une couche de robustesse métier avec la gestion des types BigQuery. Les valeurs de filtres sont converties en fonction du type de la colonne cible : entier, flottant, booléen, date, datetime, timestamp ou numeric. Enfin, la limite de lignes n'est jamais laissée librement au client : si elle n'est pas fournie, la valeur par défaut est appliquée, sinon elle est bornée par max_limit avant d'être injectée comme paramètre SQL. Au final, l'API expose donc une interface simple pour le front, mais s'appuie en interne sur une implémentation rigoureuse en termes de validation, de sécurisation et de gestion des erreurs.

Une évolution importante a consisté à exposer plusieurs couches de données via un paramètre layer. L'API peut désormais interroger les tables raw, silver ou gold selon le besoin. Cette évolution a été utilisée pour servir les nouvelles tables meteo_by_city et air_quality_by_city, avec deux usages distincts : des données silver détaillées pour les lectures fines ou cartographiques, et des données gold quotidiennes pour les synthèses et les indicateurs consolidés. FastAPI joue donc désormais un rôle d'abstraction entre plusieurs granularités de restitution et pas seulement un rôle d'accès au dataset gold par défaut.

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

Ce point est important pour un projet professionnalisant : les entrées utilisateurs sont contrôlées et les erreurs remontées proprement.

Le service BigQuery montre aussi une vraie attention à la sécurisation des requêtes.

### Extrait de code 6 - Construction de filtres BigQuery sécurisés

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

L'usage de paramètres plutôt que d'une concaténation naïve des valeurs est un bon indicateur de maturité technique.





9. Frontend Streamlit et restitution
 

Le front Streamlit propose une navigation entre plusieurs pages thématiques. Le code de la page d'accueil montre un travail de présentation, de structuration et de séparation des responsabilités.

Le front charge les données à la demande, page par page, ce qui limite le cout de chargement initial. Cela montre une réflexion sur les performances et l'ergonomie.

Le tableau de bord n'est donc pas seulement démonstratif : il sert de couche de lecture fonctionnelle au-dessus de l'API.

Le front a été enrichi par une cinquième page dédiée à l'observatoire environnemental. Cette page croise des données météo et des données de qualité de l'air pour une ville choisie. L'implémentation repose sur une stratégie hybride cohérente avec les tables dbt créées : la météo reste consommée en silver afin de conserver la granularité horaire nécessaire aux courbes, tandis que la synthèse quotidienne de qualité de l'air est consommée en gold pour alimenter les KPI et la heatmap. La carte ATMO détaillée, qui nécessite encore les coordonnées et le niveau par zone, reste quant à elle branchée sur la couche silver. Cette évolution montre un vrai travail de conception de contrat de données entre dbt, FastAPI et Streamlit.









10. Prédiction et machine learning
 
Le dossier predict constitue une brique autonome du projet. Il repose notamment sur :

- scikit-learn ;
- mlflow ;
- un prétraitement dédié ;
- un modèle de régression linéaire ;
- des métriques d'évaluation.

Cette brique n'est pas un simple script de démonstration. Le code montre une chaine ML complète, depuis l'extraction des données de travail dans BigQuery jusqu'a la production d'une prédiction exploitable. Le module train.py orchestre ce cycle en chargeant les données depuis les tables gold, en construisant les jeux d'entrainement et de test, puis en appelant les différentes étapes du moteur de prédiction. La séparation entre chargement, prétraitement, apprentissage, évaluation et inférence rend l'ensemble plus lisible et plus facilement industrialisable.

La source des données d'apprentissage est clairement identifiée dans data.py. Les requêtes SQL ciblent les tables nat_tr_predi et reg_tr_predi produites en amont par dbt, ce qui montre une articulation nette entre la couche analytique et la couche machine learning. Le module sait charger soit l'historique complet pour l'entrainement, soit un sous-ensemble récent pour préparer une prédiction. Cette organisation est importante, car elle évite de dupliquer la logique de préparation des variables entre SQL et Python.

Le prétraitement est pris en charge par une pipeline scikit-learn déclarée dans preproc.py. Cette pipeline combine un KNNImputer pour traiter les valeurs manquantes et un StandardScaler pour normaliser les variables numériques. Le choix d'un ColumnTransformer permet de sélectionner automatiquement les colonnes numériques et de produire un DataFrame prétraité cohérent avec les attentes du modèle. Dans model.py, ce préprocesseur est ajusté sur les données d'entrainement puis sauvegarde comme artefact distinct, avant d'être recharge pour transformer les données de test ou de prédiction. Cette séparation entre préprocesseur et modèle est une bonne pratique, car elle garantit la cohérence entre apprentissage et inférence.

Le modèle retenu est une régression linéaire de scikit-learn, encapsulée dans la classe Energypredict. La méthode create_model instancie LinearRegression puis journalise ses hyperparamètres. L'entrainement est ensuite effectue par train_model, qui ajuste le modèle sur les données prétraitées et l'enregistre sous le nom energy_pred. Ce choix de modèle reste simple, mais il est pertinent dans un projet pédagogique et professionnalisant, car il permet d'obtenir une baseline interprétable tout en mettant l'accent sur la structuration du pipeline global.

L'évaluation est également explicite dans le code. La méthode evaluate_model calcule quatre métriques complémentaires : MAE, MSE, R2 et MAPE. Ce choix est intéressant, car il permet de croiser une lecture absolue de l'erreur, une pénalisation quadratique des écarts, un indicateur de qualité globale d'ajustement et une mesure relative en pourcentage. Les résultats sont journalises via l'objet MlFlowLogger, ce qui donne au projet une dimension de suivi d'expérimentation au-delà d'un simple affichage console.

La journalisation ML est en effet un point fort de cette brique. Le module mllogs.py configure Mlflow, ouvre un run, associe les exécutions à une expérience mensuelle et enregistre à la fois les hyperparamètres, les métriques et les artefacts de modèle. Le préprocesseur et le modèle sont chacun sauvegardes avec un nom versionnable, puis rechargeables via Mlflow lors de l'inférence. Cette approche montre que le projet ne se limite pas à entrainer un modèle une fois, mais qu'il prépare aussi sa réutilisation et sa traçabilité dans le temps.

Enfin, la prédiction en elle-même est pensée comme un flux distinct de l'entrainement. Les fonctions build_input_national et build_input_region construisent une observation à prédire à partir du contexte temporel courant, des consommations récentes et de variables dérivées comme prev_conso_mean, prev_conso_mean_h ou prev_conso_mean_m. Le système recharge ensuite le préprocesseur et le modèle enregistres avant de produire une estimation de consommation. Cet enchainement montre que le projet couvre l'ensemble du cycle ML utile en production : préparation des features, apprentissage, évaluation, stockage des artefacts et inférence sur de nouvelles données.


### Extrait de code 7 - Entrainement et évaluation du modèle

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

Ces extraits montrent que le projet integre un vrai cycle ML : préparation des données, entrainement, évaluation, journalisation et réutilisation des artefacts.

11. Infrastructure as Code et industrialisation
 

L'infrastructure est décrite via Terraform. Le fichier iac/main.tf montre un niveau de détail significatif : projet GCP, services, comptes de service, bucket, registres d'artefacts et droits IAM.

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
  description  = "Service account dédié a Airflow pour consommer les artefacts du projet."
}
```

Ce volet infrastructure renforce très clairement la valeur du projet pour la création, la mise en place de l’infrastructure, son déploiement et sa réutilisabilité. Il montre une capacité à penser exploitation, sécurité et déploiement, modularité avec les ressources adaptées et modifiables à l’infini sans saisir une seule ligne de code.

12. Qualité logicielle et tests

Le dépôt contient des tests unitaires dans plusieurs sous-projets. Cette présence est importante car elle montre un souci de vérification et de robustesse.
Les tests ne sont pas limites à des cas superficiels. Ils couvrent plusieurs couches de l'architecture et vérifient aussi bien des comportements fonctionnels que des cas d'erreur ou des choix d'implémentation. Cette largeur de couverture est importante dans un projet de type data platform, car elle permet de fiabiliser des composants hétérogènes : appels HTTP, construction de requêtes SQL, chargement BigQuery et orchestration Airflow.

Le sous-projet FastAPI contient par exemple des tests unitaires sur le service d'accès BigQuery. Le fichier test_bigquery_service.py vérifie que les tables masquées ne sont pas exposées par défaut, que les colonnes d'une table sont correctement restituées et surtout que les requêtes sont construites de façon sure. Un test contrôle explicitement la présence de paramètres nommes comme @filter_0, @filter_1 et @limit_value dans la requête SQL générée, ce qui constitue une preuve concrète de protection contre une construction naïve des filtres.

Le module d'ingestion est également testé sur des scenarios nominaux et non nominaux. Dans test_eco2mix_ingest.py, des réponses HTTP factices sont injectées pour simuler un succès CSV, un content-type inattendu ou encore un dépassement de quota avec code 429. Ce choix est pertinent, car il permet de tester la logique défensive de l'ingestion sans dépendre d'un accès réel à l'API ODRE. Le comportement attendu, comme le retour d'un dictionnaire vide en cas de rate limiting, est ainsi vérifié de manière déterministe.

La partie chargement vers BigQuery fait elle aussi l'objet de tests cibles. Le fichier test_bigquery_loader.py vérifie que les fichiers sont charges avec la bonne table cible, le bon délimiteur et la bonne politique d'écriture. Un test montre également qu'en cas d'échec de chargement avec le schéma initial, le système retente avec un schéma converti en STRING. Cette stratégie est intéressante, car elle traduit une logique de résilience face à des variations de format ou de typage dans les fichiers sources.

Enfin, les DAGs Airflow eux-mêmes sont testés. Le fichier test_dag_eco2mix_national_tr.py n'exécute pas un environnement Airflow complet, mais installe des stubs permettant de vérifier la structure du DAG, ses tags, ses tâches déclarées et ses expressions cron. Ce point est important, car il montre que la qualité logicielle porte aussi sur l'orchestration et pas uniquement sur les modules Python classiques. Le projet valide ainsi non seulement le code de traitement, mais aussi la forme attendue des pipelines qui pilotent la chaine globale.

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

13. Compétences mobilisées et en adéquation avec le bloc RNCP

Au regard du contenu du dépôt et de l'architecture, plusieurs compétences attendues dans un bloc de certification de type RNCP sont mobilisées :

- analyse d'un besoin et découpage en sous-systèmes ;
- conception d'une architecture logicielle modulaire ;
- développement Python back-end ;
- traitement et préparation de données ;
- modélisation analytique SQL ;
- orchestration de flux de traitement ;
- exposition de services API ;
- conception d'une interface de restitution ;
- mise en place de tests ;
- infrastructure as code et déploiement cloud.

Le projet ne repose pas sur une seule compétence, mais sur une articulation entre développement, data engineering, API, visualisation, machine learning et DevOps.

14. Difficultés techniques et enjeux réussis

Au vu de la structure du projet, plusieurs difficultés techniques ont été traitées :

- hétérogénéité des sources de données ;
- synchronisation de traitements dépendants ;
- gestion de l'exposition sécurisée des données analytiques ;
- préparation de features temporelles pertinentes ;
- conservation d'une architecture lisible malgré la multiplicité des briques ;
- industrialisation de l'environnement cible dans GCP.

La qualité du dépôt montre que le projet a été pensé sur la durée, avec une logique de structuration progressive.

15. Résultats et valeur produite

Le projet Mix Energy produit plusieurs résultats concrets :

- une chaine de collecte et de transformation exploitable ;
- des tables analytiques orientées métier ;
- un calcul de KPIs autour de la production, du mix et du CO2 ;
- une API de consultation des données ;
- une interface utilisateur de restitution ;
- une base technique pour des prédictions de consommation ;
- une infrastructure de déploiement cloud.

Ces livrables montrent une cohérence de bout en bout. Le projet ne se limite pas à un exercice de code : il correspond à un système d'information data complet, structure et industrialisable.

16. Conclusion

Le projet Mix Energy constitue une preuve solide de travail de fond pour une évaluation par jury avant soutenance. Il couvre un spectre technique large et cohérent : ingestion, orchestration, transformation analytique, API, visualisation, prédiction et infrastructure cloud.

L'intérêt principal du projet est sa dimension complète. Il ne s'agit pas d'une démonstration isolée, mais d'une architecture multi-composants reliée par un objectif métier clair. Les fichiers du dépôt montrent un travail structure, testable, documente par le code et appuyé sur des technologies reconnues du monde professionnel.

Pour une certification RNCP37827BC01, ce dossier permet donc de mettre en avant une démarche de conception, de réalisation et d'industrialisation logicielle avec une vraie profondeur technique.

17. Annexes - fichiers principaux du dépôt

### Composants orchestration

- airflow/dags/dag_base_carbone.py
- airflow/dags/dag_eco2mix_national_tr.py
- airflow/dags/dag_eco2mix_national_cons_def.py
- airflow/dags/dag_eco2mix_regional_tr.py
- airflow/dags/dag_eco2mix_regional_cons_def.py
- airflow/dags/dag_meteo.py
- airflow/dags/dag_air_quality.py
- airflow/dags/dag_train_model.py
- airflow/docker-compose.yaml

### Composants data

- ingest_dbt/src/mix_energy/eco2mix_ingest.py
- ingest_dbt/src/mix_energy/base_carbone_ingest.py
- ingest_dbt/src/mix_energy/meteo_ingest.py
- ingest_dbt/src/mix_energy/air_quality_ingest.py
- ingest_dbt/src/mix_energy/bucket_to_bigquery_airflow.py
- dbt/models/silver/eco2mix_national_cons_def_histo.sql
- dbt/models/silver/eco2mix_regional_cons_def_histo.sql
- dbt/models/silver/meteo_by_city.sql
- dbt/models/silver/air_quality_by_city.sql
- dbt/models/gold/nat_cons_agre_j.sql
- dbt/models/gold/nat_tr_agre_j.sql
- dbt/models/gold/nat_tr_predi.sql
- dbt/models/gold/reg_cons_agre_j.sql
- dbt/models/gold/reg_tr_agre_j.sql
- dbt/models/gold/reg_tr_predi.sql
- dbt/models/gold/kpi.sql
- dbt/models/gold/gold_meteo_by_city.sql
- dbt/models/gold/gold_air_quality_by_city.sql

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
- front-streamlit/dashboard/pages/5_environnement.py

### Prédiction et infrastructure

- predict/src/predict/train.py
- predict/src/predict/model.py
- predict/src/predict/preproc.py
- iac/main.tf
- iac/provider.tf
- iac/variables.tf
Captures d’écran de streamlit pour montrer les dashboard visuels pour les données nationales et régionales :
Page d’accueil de l’application déployée sur streamlit :
 

Dashboard national historique :
 

Dashboard national temps réel :
 

Dashboard régional historique :
 



Dashboard régional temps réel :
 


