variable "TF_VAR_gcp_user_email" {
  type        = string
  description = "Adresse e-mail de l'utilisateur principal pour l'attribution IAM (ex: user@domaine.com)"
}
variable "TF_VAR_org_id" {
  type        = string
  description = "ID de l'organisation GCP (ex: 123456789012)"
}

variable "TF_VAR_billing_account" {
  type        = string
  description = "ID du compte de facturation GCP (ex: 01A1B2-123456-7890AB)"
}
variable "TF_VAR_vm_name" {
  description = "Nom de l'instance VM"
  type        = string
  default     = "vm-mix-energie"
}

variable "TF_VAR_vm_zone" {
  description = "Zone de déploiement de la VM"
  type        = string
  default     = "europe-west1-b"
}

variable "TF_VAR_vm_machine_type" {
  description = "Type de machine de la VM"
  type        = string
  default     = "e2-micro"
}

variable "TF_VAR_vm_network_name" {
  description = "Nom du reseau VPC attache a la VM"
  type        = string
  default     = "mix-energy-network"
}

variable "TF_VAR_vm_subnetwork_name" {
  description = "Nom du sous-reseau attache a la VM"
  type        = string
  default     = "mix-energy-subnetwork"
}

variable "TF_VAR_vm_subnetwork_region" {
  description = "Region du sous-reseau de la VM"
  type        = string
  default     = "europe-west1"
}

variable "TF_VAR_vm_subnetwork_cidr" {
  description = "Plage CIDR du sous-reseau de la VM"
  type        = string
  default     = "10.12.0.0/24"
}

variable "TF_VAR_vm_image_family" {
  description = "Famille d'image pour le disque boot"
  type        = string
  default     = "debian-11"
}

variable "TF_VAR_vm_image_project" {
  description = "Projet de l'image pour le disque boot"
  type        = string
  default     = "debian-cloud"
}
variable "TF_VAR_location" {
  type        = string
  description = "Location where the GCP resources will be created for mix-energy"
  default     = "EU"
}

variable "TF_VAR_artifact_registry_location" {
  type        = string
  description = "Region used for Artifact Registry repositories."
  default     = "europe-west1"
}

variable "TF_VAR_project_id" {
  type        = string
  description = "GCP project id where the resources will be created into."
}

variable "TF_VAR_project_name" {
  type        = string
  description = "Human-readable GCP project name."
}

variable "TF_VAR_project_bucket_name" {
  type        = string
  description = "Bucket name managed in the target project."
}

variable "TF_VAR_bootstrap_only" {
  type        = bool
  description = "When true, only create the GCP project and required APIs."
  default     = false
}

variable "TF_VAR_create_demo_resources" {
  type        = bool
  description = "When true, create the demo BigQuery dataset and table used for Terraform smoke tests."
  default     = true
}
