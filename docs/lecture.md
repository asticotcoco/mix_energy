



Voici le parcours de lecture que je te recommande pour comprendre le pipeline de bout en bout, dans le bon ordre.

README.md
Point d’entrée du projet. Il donne la structure des modules et montre déjà la chaîne globale entre ingestion, orchestration, transformation, API et front.

rapport_rncp37827BC01_mix_energy.md
C’est le document le plus utile pour comprendre l’architecture complète. Il décrit clairement le flux ingestion → stockage → dbt → FastAPI → Streamlit, avec le contexte métier et les couches techniques.

README.md
À lire pour comprendre comment le pipeline est orchestré côté Airflow, comment les DAGs s’exécutent, et comment l’environnement local est démarré.

README.md
À lire juste après Airflow pour comprendre la couche de transformation dans BigQuery, la logique des targets dev/prod, et le rôle des modèles dbt entre données brutes et tables exposées.

README.md
Couvre la couche d’exposition. Tu y vois les endpoints disponibles, la façon dont les tables gold sont interrogées, et les endpoints de prédiction.

README.md
Dernière étape du pipeline. Ce fichier montre comment Streamlit consomme l’API FastAPI et comment la visualisation est configurée.

En complément, tu peux lire rapport_rncp37827BC01_mix_energy_soutenance.md si tu veux une version plus synthétique et plus narrative du projet.

À ne pas prioriser :

README.md est vide
README.md est vide
Donc pour l’ingestion réelle et la partie modèle, la doc Markdown ne suffit pas : il faudra ensuite passer au code.
Donc si ton objectif est de bien comprendre le pipeline plus l’infra, l’ordre devient : README.md → rapport_rncp37827BC01_mix_energy.md → README.md → README.md → README.md → README.md, avec Terraform compris surtout via le rapport. Pour Terraform en détail, les fichiers Markdown ne suffisent pas : il faudra ensuite lire le code dans iac, surtout main.tf, provider.tf, variables.tf et deploy_gcp_project.sh.

Si tu veux, je peux maintenant te faire la liste complète des fichiers non-Markdown à lire pour comprendre précisément la partie Terraform.
Oui. Après les Markdown, je te conseille ce parcours Python, toujours dans l’ordre réel du pipeline.

Ordre de lecture

dag_eco2mix_national_tr.py
C’est le meilleur point d’entrée pour comprendre le flux complet orchestré : récupération CSV, upload GCS, transfert BigQuery, précheck dbt, exécution dbt.

dag_base_carbone.py
Montre le même schéma sur une autre source, avec ingestion DataFrame puis dépôt dans le bucket.

eco2mix_ingest.py
À lire juste après les DAGs pour comprendre la récupération côté source ODRE : appel HTTP, gestion des statuts, export CSV.

base_carbone_ingest.py
Pour la logique spécifique Base Carbone ADEME.

meteo_ingest.py
Pour l’enrichissement météo du pipeline.

air_quality_ingest.py
Pour la partie qualité de l’air si tu veux comprendre les sources annexes.

bucket_to_bigquery.py
C’est le pivot entre GCS et BigQuery : listing des blobs, filtrage, génération des schémas, appel du loader.

bigquery_loader.py
Le vrai cœur du chargement BigQuery : délimiteurs, schémas, retries, fallback STRING, tracking des fichiers chargés.

bigquery_schema_generator.py
À lire juste après le loader pour comprendre comment les schémas sont inférés avant chargement.

bucket_to_bigquery_airflow.py
Petit fichier, mais utile pour voir l’adaptation de la logique GCS → BigQuery au contexte Airflow.

airflow_dbt.py
Très important pour le lien entre ingestion Python et transformation dbt : target, datasets attendus, commande dbt construite côté DAG.

main.py
Point d’entrée de l’exposition API : routes, parsing des filtres, endpoints de prédiction.

bigquery_service.py
Le vrai cœur métier côté API : découverte des tables, validation des colonnes, construction sécurisée des requêtes BigQuery.

config.py
Pour comprendre quelles variables d’environnement pilotent l’API.

schemas.py
Pour voir le contrat des payloads exposés au front.

train.py
Important parce que l’API appelle directement la prédiction depuis ici.

data.py
À lire ensuite pour comprendre quelles tables BigQuery alimentent le modèle et comment les features sont construites.

model.py
Pour l’implémentation du modèle et du prétraitement.

data_api_client.py
C’est le meilleur point d’entrée côté front : on voit exactement comment Streamlit consomme FastAPI.

dashboard_app.py
Pour la structure générale de l’application Streamlit.

1_national_historique.py
Première page métier à lire, car elle montre un cas d’usage complet de consommation API côté visualisation.

2_national_temps_reel.py
Puis la variante temps réel.

3_regional_historique.py
Même logique, côté régional.

4_regional_temps_reel.py
Dernière couche de restitution.

Point important
La couche dbt elle-même n’est pas portée par des fichiers Python centraux. Après airflow_dbt.py, la source de vérité passe surtout par :

schema.yml
nat_tr_agre_j.sql
nat_tr_predi.sql
reg_tr_agre_j.sql
reg_tr_predi.sql
À lire plus tard
chargement_bigquery.py
Je le mettrais après tout ça. C’est utile comme script local ou de support, mais ce n’est pas la pièce principale du pipeline orchestré actuel, qui passe surtout par ingest_dbt et Airflow.