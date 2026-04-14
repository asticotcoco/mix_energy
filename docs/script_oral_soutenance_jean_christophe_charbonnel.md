# Script oral de soutenance

## Candidat

- Nom : Charbonnel
- Prenom : Jean-Christophe
- Centre de formation : Artefact
- Projet : Mix Energy
- Bloc : RNCP37827BC01

## Usage du script

Ce script est concu pour accompagner une presentation orale page par page. Il ne doit pas etre lu mot a mot de facon mecanique, mais servir de fil conducteur pour garder un discours fluide, structuré et maitrise devant le jury.

Le ton attendu est simple : phrases courtes, vocabulaire precis, transitions nettes, et mise en avant du lien entre besoin metier, architecture technique et valeur produite.

## Page 1 - Titre et accroche

Bonjour, je vais vous presenter notre projet Mix Energy, realise dans le cadre du bloc RNCP37827BC01.

L'objectif de ce projet est de construire une chaine de traitement de donnees autour du mix electrique francais, afin de collecter, transformer, analyser et restituer des donnees energetiques dans un cadre a la fois metier, technique et evolutif.

Le sujet nous a interesses parce qu'il est immediatement comprehensible, tres visuel, et directement relie a des enjeux actuels comme la transition energetique, le pilotage de la consommation et l'empreinte carbone.

Aujourd'hui, je vais montrer comment nous avons transforme ce besoin en une solution data de bout en bout, avec ingestion, orchestration, transformation, exposition par API, visualisation et premiere brique predictive.

## Page 2 - Objet du document et fil directeur

Cette presentation suit le meme fil directeur que le rapport remis au jury.

Je vais d'abord rappeler le besoin metier et la cible fonctionnelle du projet.

Je presenterai ensuite l'architecture retenue, les principales briques techniques et le flux de donnees complet.

Je terminerai par les preuves concretes de travail de fond visibles dans le depot, puis par la valeur produite et les perspectives d'evolution.

L'idee n'est pas seulement de montrer un assemblage d'outils, mais de demonstrer une demarche coherente de conception et d'industrialisation.

## Page 3 - Cadrage metier

Le projet porte sur le mix electrique francais et son empreinte carbone.

L'objectif metier principal est de recuperer des donnees de production et de consommation, de calculer des indicateurs utiles, notamment autour du CO2, et de les restituer dans un tableau de bord national et regional.

Nous avons egalement integre une dimension predictive. Le projet prepare une logique de prediction de la consommation, avec un premier socle fonde sur les donnees energie, et une perspective d'enrichissement par la meteo et d'autres sources contextuelles.

Ce point est important parce qu'il montre que le projet n'est pas uniquement descriptif. Il cherche aussi a ouvrir vers l'anticipation et l'aide a la decision.

## Page 4 - Pourquoi ce projet

Nous avons retenu ce sujet pour trois raisons principales.

La premiere, c'est qu'il repond a un cas metier tres lisible. Le jury peut tout de suite comprendre l'interet de suivre la production electrique, la consommation et l'empreinte carbone.

La deuxieme, c'est sa valeur visuelle. Les evolutions du mix, les comparaisons entre national et regional, ou encore la lecture des KPIs se pretent bien a un dashboard.

La troisieme, c'est sa valeur professionnelle. Ce type de projet parle directement a des acteurs du secteur energie et illustre des competences data tres concretes.

## Page 5 - Sources de donnees

Le coeur du projet repose sur les jeux de donnees Eco2mix via ODRE.

Nous utilisons les jeux nationaux et regionaux, en temps reel et en version consolidee. Cela permet d'avoir a la fois des donnees fraiches pour le suivi operationnel et des donnees stabilisees pour l'analyse historique.

Nous ajoutons egalement une logique metier avec la Base Carbone ADEME, qui fournit les facteurs d'emission necessaires au calcul de l'empreinte carbone.

Dans la vision cible, nous pouvons enrichir le dispositif avec des donnees meteo et des donnees de qualite de l'air, afin d'augmenter la valeur analytique et predictive du projet.

## Page 6 - Architecture fonctionnelle

Le fonctionnement global du projet suit une logique en plusieurs temps.

D'abord, une phase d'initialisation permet de charger les historiques et les referentiels.

Ensuite, des traitements recurrents viennent alimenter les donnees du jour ou du mois.

Puis, des transformations analytiques structurent les donnees en tables exploitables pour les usages metier, le dashboard et la prediction.

Cette organisation montre que nous avons pense le projet comme un pipeline complet, et pas comme une suite de scripts isoles.

## Page 7 - Architecture technique globale

Sur le plan technique, l'architecture s'articule autour de plusieurs briques specialisees.

Airflow orchestre les traitements.

dbt transforme les donnees et construit les couches analytiques.

BigQuery sert d'entrepot de donnees.

FastAPI expose les donnees sous forme de service read-only.

Streamlit fournit la restitution visuelle.

Enfin, Terraform prepare l'infrastructure cloud sur GCP.

Cette decomposition nous a permis de separer clairement les responsabilites et de rendre l'ensemble plus maintenable.

## Page 8 - Ingestion des donnees

Le travail d'ingestion est une vraie brique du projet.

Nous ne nous sommes pas contentes d'appeler une API de facon ideale. Le code gere plusieurs statuts HTTP, prend en compte les erreurs reseau, les problemes d'autorisation et les limites d'appel.

Cette partie est importante parce qu'elle montre une logique defensive et une approche realiste de l'integration de sources externes.

Autrement dit, nous avons travaille sur la robustesse du pipeline des l'entree des donnees.

## Page 9 - Orchestration Airflow

Airflow nous permet de planifier, ordonner et fiabiliser les traitements.

Les DAGs assurent la verification des prerequis, l'ingestion, le transfert vers BigQuery, puis l'execution des transformations.

Nous avons aussi une DAG dediee a l'entrainement des modeles.

Ce point montre que le projet repose sur une orchestration formelle et non sur des executions manuelles ou fragiles.

## Page 10 - Transformations dbt

dbt constitue l'une des preuves les plus fortes du travail de fond.

Les donnees sont nettoyees, homogenisees puis transforme es dans des modeles SQL clairement structures.

Nous avons distingue des couches de travail, avec une logique silver pour la preparation et une logique gold pour les tables de restitution et les usages aval.

Cette structuration permet de mieux tracer la logique metier, de fiabiliser les traitements et de rendre l'ensemble plus lisible pour un tiers.

## Page 11 - KPIs et logique metier

Le projet ne se limite pas a stocker des donnees. Il produit des indicateurs metier utiles.

Par exemple, nous calculons des agr egats de production et des ratios sur la part du nucleaire, du thermique, du renouvelable, ainsi que des indicateurs lies au taux de CO2.

Ces calculs donnent une lecture concrete du mix electrique et montrent la capacite du projet a transformer des donnees brutes en information decisionnelle.

## Page 12 - API FastAPI

L'API FastAPI joue un role central dans l'architecture.

Elle se place entre l'entrepot analytique et la couche de visualisation.

Elle permet de lister les tables, de decrire les colonnes et d'interroger les donnees avec des filtres, tout en controlant les entrees et en gerant les erreurs.

Ce choix montre une vraie separation des couches et une volonte de rendre la donnee reutilisable dans plusieurs contextes.

## Page 13 - Dashboard Streamlit

Le front Streamlit fournit la restitution visuelle du projet.

Il propose plusieurs vues, notamment nationale, regionale, historique et temps reel.

Le front ne charge pas tout en bloc. Il interroge l'API page par page, ce qui rend l'experience plus legere et plus ciblee.

Cette couche est importante pour la soutenance, parce qu'elle permet de montrer tres concre tement la valeur finale produite a partir du pipeline.

## Page 14 - Prediction et machine learning

Le projet comprend egalement une brique machine learning.

Nous avons mis en place un pipeline de prediction avec pretraitement, entrainement, evaluation et journalisation des metriques.

Cette partie montre que le projet ne reste pas uniquement sur de la collecte et de la restitution. Il ouvre vers un usage plus avance d'anticipation de la consommation.

Elle renforce egalement la coherence entre la preparation des donnees, les transformations analytiques et les usages data science.

## Page 15 - Infrastructure et industrialisation

L'infrastructure est geree par Terraform sur GCP.

Cela comprend la creation du projet, l'activation des services, la gestion des comptes de service, le bucket de stockage et d'autres ressources necessaires.

Cette partie est essentielle, parce qu'elle montre que le projet a ete pense dans une logique d'exploitation, de securite et de deploiement, et pas seulement comme un exercice local.

## Page 16 - Qualite et tests

Le depot contient plusieurs tests unitaires sur les briques critiques, par exemple sur l'ingestion, les DAGs et le service BigQuery expose par l'API.

La presence de ces tests montre que nous avons pris en compte des cas non nominaux et que nous avons cherche a fiabiliser l'ensemble.

Pour le jury, c'est un indicateur important de maturite, car il montre un souci de verification et de robustesse.

## Page 17 - Competences mobilisees

Ce projet mobilise plusieurs familles de competences.

Il couvre l'analyse d'un besoin, la conception d'architecture, le developpement Python, les traitements SQL, l'orchestration, l'exposition d'API, la visualisation, le machine learning et l'infrastructure cloud.

Autrement dit, il s'agit d'un projet complet qui permet de montrer une vraie capacite de liaison entre software engineering, data engineering, data visualisation et DevOps.

## Page 18 - Valeur produite

La valeur produite par le projet peut se resumer en quelques points.

Nous avons construit une chaine de collecte et de transformation exploitable.

Nous avons produit des tables orientees metier et des KPIs lisibles.

Nous avons expose ces donnees via une API puis un dashboard.

Nous avons enfin prepare une base solide pour les usages predictifs et les evolutions futures.

## Page 19 - Conclusion orale impactante

Pour conclure, je dirais que Mix Energy est un projet qui vaut a la fois par sa lisibilite metier, par sa profondeur technique et par sa credibilite d'evolution.

Il ne s'agit pas simplement d'avoir assemble Airflow, dbt, FastAPI et Streamlit. Le vrai enjeu etait de construire une solution coherente, capable de relier un besoin metier clair a une chaine technique complete et defendable.

Ce projet montre notre capacite a traiter un sujet data de bout en bout : recuperer la donnee, l'organiser, la transformer, l'exposer, la visualiser et preparer son usage predictif.

Dans le cadre du RNCP37827BC01, il constitue donc une preuve concrete de travail de fond, de rigueur technique et de capacite a produire une solution utile, structuree et industrialisable.

Je vous remercie pour votre attention, et je suis maintenant disponible pour repondre a vos questions.

## Conseils d'oral

- Garder un debit calme et regulier.
- Marquer une courte pause entre chaque page ou idee forte.
- Ne pas lire les extraits de code en detail : les commenter a un niveau fonctionnel.
- Revenir systematiquement au lien entre besoin metier, architecture et valeur produite.
- En cas de question technique, partir du concret : source de donnees, DAG, table dbt, endpoint API, dashboard, prediction.