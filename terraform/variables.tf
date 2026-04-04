# terraform/variables.tf

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "machine_type" {
  description = "VM machine type. e2-standard-4 = 4 vCPU 16GB RAM"
  type        = string
  default     = "e2-standard-4"
}

variable "vm_user" {
  description = "Linux user en la VM"
  type        = string
  default     = "ubuntu"
}

variable "repo_url" {
  description = "URL del repositorio Git del proyecto"
  type        = string
  default     = "https://github.com/tu-usuario/capstone-support-analytics"
}
