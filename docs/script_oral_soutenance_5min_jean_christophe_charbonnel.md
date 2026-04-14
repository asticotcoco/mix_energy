# Script oral de soutenance 5 minutes

## Candidat

- Nom : Charbonnel
- Prenom : Jean-Christophe
- Centre de formation : Artefact
- Projet : Mix Energy
- Bloc : RNCP37827BC01

## Introduction - 30 secondes

Bonjour, je vais vous presenter notre projet Mix Energy, realise dans le cadre du bloc RNCP37827BC01.

L'objectif etait de construire une chaine de traitement de donnees autour du mix electrique francais, afin de collecter des donnees energie, de les transformer, de calculer des indicateurs metier comme l'empreinte carbone, puis de les restituer dans un dashboard.

Ce projet nous a interesses parce qu'il combine un besoin metier clair, une forte dimension visuelle et une vraie profondeur technique.

## 1. Besoin metier - 40 secondes

Le besoin metier principal consiste a suivre la production et la consommation electriques, a lire leur evolution dans le temps et a produire des indicateurs interpretable s, notamment autour du mix energetique et du CO2.

Le projet prepare aussi une logique d'anticipation, avec une brique de prediction de la consommation. L'idee est d'abord de s'appuyer sur les donnees energie, puis d'enrichir la prediction avec des donnees meteorologiques.

Autrement dit, nous ne sommes pas restes sur un simple projet de visualisation. Nous avons construit un socle qui peut evoluer vers l'aide a la decision.

## 2. Architecture globale - 1 minute

Notre architecture repose sur plusieurs briques specialisees.

L'ingestion recupere les donnees depuis les jeux Eco2mix via ODRE, ainsi que les facteurs d'emission de la Base Carbone ADEME.

Airflow orchestre les traitements et planifie les differentes etapes.

BigQuery sert d'entrepot de donnees.

dbt transforme les donnees, les nettoie et construit les tables analytiques utiles au suivi et a la prediction.

FastAPI expose ensuite les donnees sous forme de service read-only.

Enfin, Streamlit fournit la restitution visuelle a travers plusieurs vues nationales et regionales.

L'ensemble est complete par Terraform pour l'infrastructure GCP.

## 3. Flux de donnees et travail technique - 1 minute

Le flux est le suivant : nous recuperons les donnees externes, nous les deposons dans le stockage, nous les chargeons dans BigQuery, nous les transformons avec dbt, puis nous les exposons via FastAPI avant de les afficher dans Streamlit.

Le travail de fond se voit a plusieurs niveaux.

D'abord dans l'ingestion, avec une gestion explicite des statuts HTTP et des erreurs d'appel API.

Ensuite dans Airflow, avec des DAGs qui structurent les executions et fiabilisent le pipeline.

Puis dans dbt, avec un vrai travail de transformation analytique, de calcul de KPIs et de preparation des donnees pour les usages aval.

Nous avons donc travaille a la fois la robustesse, la structuration et l'exploitabilite de la donnee.

## 4. API, dashboard et prediction - 50 secondes

Une fois les donnees preparees, l'API FastAPI permet de les rendre accessibles de facon propre et reutilisable.

Le dashboard Streamlit consomme cette API et restitue plusieurs vues, notamment historiques et temps reel, au niveau national et regional.

Nous avons aussi integre une premiere brique machine learning, avec pretraitement, entrainement, evaluation et journalisation de metriques.

Cela montre que le projet ne s'arrete pas a l'observation des donnees, mais ouvre deja sur leur exploitation predictive.

## 5. Valeur du projet - 40 secondes

La valeur du projet tient a trois points.

Le premier, c'est sa lisibilite metier. Le sujet est concret, actuel et facile a comprendre.

Le deuxieme, c'est sa coherence technique. Chaque composant a un role clair dans une architecture de bout en bout.

Le troisieme, c'est sa capacite d'evolution. Le socle actuel permet deja d'envisager des enrichissements autour de la meteo, de la qualite de l'air, de la prediction a J+1 et d'une industrialisation plus poussee.

## Conclusion - 40 secondes

Pour conclure, Mix Energy est un projet qui montre notre capacite a transformer un besoin metier en solution data complete.

Nous avons construit une chaine qui va de la collecte a la restitution, en passant par l'orchestration, la transformation analytique, l'exposition via API et la premiere logique predictive.

Dans le cadre du RNCP37827BC01, ce projet constitue donc une preuve concrete de travail de fond, de rigueur technique et de capacite a concevoir une solution utile, structuree et defendable.

Je vous remercie pour votre attention, et je suis disponible pour repondre a vos questions.

## Conseils d'usage

- Viser un debit calme et regulier.
- Marquer une pause apres chaque grand bloc.
- Illustrer oralement avec un ou deux exemples concrets plutot que trop de details techniques.
- Si le jury pose une question, revenir au triptyque besoin metier, architecture, valeur produite.