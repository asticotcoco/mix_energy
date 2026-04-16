# Terraform Mix Energy

Ce dossier contient l'infrastructure as code du projet Mix Energy pour Google Cloud Platform.

L'objectif est de provisionner le socle cloud utilise par le pipeline de donnees : projet GCP, APIs principales, comptes de service, bucket GCS, datasets BigQuery, repositories Artifact Registry, reseau VPC et VM de demonstration.

## Contenu du dossier

- main.tf : definition des ressources GCP.
- provider.tf : provider Terraform Google et backend local.
- variables.tf : variables attendues par le deploiement.
- auto.tfvars : valeurs locales du projet cible.
- deploy_gcp_project.sh : script recommande pour bootstrap + import + apply complet.
- deploy_full.sh : ancien script interactif de deploiement en deux temps.
- reset_and_import_bucket.sh : script de reinitialisation locale de l'etat puis import du bucket.

## Ressources gerees

Le code Terraform cree ou gere les ressources suivantes :

- projet GCP cible ;
- activation des APIs compute, bigquery, storage, aiplatform et artifactregistry ;
- comptes de service dedies pour import, FastAPI, bucket, BigQuery, Airflow et VM ;
- repositories Artifact Registry Docker et Python ;
- bucket GCS du projet ;
- datasets BigQuery bronze, silver et gold en dev et prod ;
- reseau VPC, sous-reseau et VM GCE.

## Variables importantes

Les variables sont declarees dans variables.tf. Les plus importantes a renseigner dans auto.tfvars sont :

- TF_VAR_project_id : identifiant du projet GCP ;
- TF_VAR_project_name : nom lisible du projet ;
- TF_VAR_project_bucket_name : nom du bucket GCS ;
- TF_VAR_org_id : identifiant de l'organisation GCP ;
- TF_VAR_billing_account : compte de facturation ;
- TF_VAR_gcp_user_email : utilisateur a qui attribuer les droits IAM de bootstrap.

Variables utiles mais optionnelles selon le contexte :

- TF_VAR_bootstrap_only : cree seulement le projet et les APIs si true ;
- TF_VAR_artifact_registry_location : region des repositories Artifact Registry ;
- TF_VAR_location : location BigQuery ;
- TF_VAR_vm_name, TF_VAR_vm_zone, TF_VAR_vm_machine_type : configuration de la VM ;
- TF_VAR_vm_network_name, TF_VAR_vm_subnetwork_name, TF_VAR_vm_subnetwork_region, TF_VAR_vm_subnetwork_cidr : configuration reseau.

## Prerequis

- Terraform installe localement ;
- gcloud installe et authentifie ;
- droits suffisants pour creer un projet GCP ou administrer le projet cible ;
- fichier auto.tfvars correctement renseigne.

Avant de lancer le deploiement, verifier l'authentification :

```bash
gcloud auth login
gcloud auth application-default login
terraform -chdir=iac init
```

## Flux recommande

Le script a privilegier est deploy_gcp_project.sh.

Il gere les cas suivants :

- bootstrap du projet si le projet GCP n'existe pas encore ;
- activation explicite des APIs ;
- attribution du role Owner a l'utilisateur de bootstrap ;
- import des ressources deja existantes avant apply ;
- apply complet avec TF_VAR_bootstrap_only=false.

Commande recommandee :

```bash
cd iac
bash deploy_gcp_project.sh
```

Ce script est prefere a deploy_full.sh, car il evite de relancer un bootstrap destructeur si le projet existe deja et reconcilie l'etat Terraform avec les ressources existantes.

## Commandes Terraform utiles

Initialisation :

```bash
terraform -chdir=iac init
```

Plan :

```bash
terraform -chdir=iac plan -var-file=auto.tfvars
```

Apply complet :

```bash
terraform -chdir=iac apply -var-file=auto.tfvars -var='TF_VAR_bootstrap_only=false'
```

Bootstrap uniquement :

```bash
terraform -chdir=iac apply -var-file=auto.tfvars -var='TF_VAR_bootstrap_only=true'
```

## Points d'attention

- Le backend Terraform est local. Les fichiers terraform.tfstate et backups restent dans ce dossier.
- Si des ressources existent deja dans GCP, utiliser de preference deploy_gcp_project.sh plutot qu'un apply brut.
- Le reseau et le sous-reseau sont geres explicitement par Terraform. La VM ne doit pas dependre du reseau par defaut du projet.
- Le bucket et les datasets sont attendus par les autres briques du pipeline, notamment Airflow, dbt et FastAPI.

## Jeux de donnees BigQuery crees

Le deploiement cree les datasets suivants :

- dev_mix_energie
- prod_mix_energie
- dev_mix_energie_silver
- prod_mix_energie_silver
- dev_mix_energie_gold
- prod_mix_energie_gold

## Quand utiliser les scripts annexes

- deploy_full.sh : seulement si tu veux conserver un deploiement interactif simple en deux etapes.
- reset_and_import_bucket.sh : utile pour reinitialiser un etat Terraform local puis reimporter le bucket existant.

## Liens avec le pipeline

Cette infrastructure supporte directement les autres composants du projet :

- Airflow utilise GCS, BigQuery et Artifact Registry ;
- dbt s'appuie sur les datasets BigQuery silver et gold ;
- FastAPI expose les tables analytiques depuis BigQuery ;
- le front Streamlit consomme l'API FastAPI ;
- le module predict peut reutiliser BigQuery et Vertex AI selon les evolutions du projet.