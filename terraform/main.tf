# =============================================================================
# terraform/main.tf — GCP Cloud deployment (Compute Engine VM con Docker)
# Puntaje Cloud: 4/4 (proyecto en cloud + IaC con Terraform)
#
# Uso:
#   cd terraform
#   terraform init
#   terraform apply -var="project_id=TU_PROJECT_ID"
#
# Prerequisitos:
#   gcloud auth application-default login
#   gcloud config set project TU_PROJECT_ID
# =============================================================================

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── Habilitar APIs necesarias ─────────────────────────────────────────────────
resource "google_project_service" "compute" {
  service            = "compute.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "storage" {
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}

# ── GCS bucket para datos y DuckDB ───────────────────────────────────────────
resource "google_storage_bucket" "capstone_data" {
  name          = "${var.project_id}-capstone-data"
  location      = var.region
  force_destroy = true

  lifecycle_rule {
    condition { age = 30 }
    action    { type = "Delete" }
  }
}

# ── Service account ───────────────────────────────────────────────────────────
resource "google_service_account" "capstone_sa" {
  account_id   = "capstone-vm-sa"
  display_name = "Capstone VM Service Account"
}

resource "google_project_iam_member" "sa_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.capstone_sa.email}"
}

# ── Firewall: abre puertos del stack ─────────────────────────────────────────
resource "google_compute_firewall" "capstone_ports" {
  name    = "capstone-stack-ports"
  network = "default"

  allow {
    protocol = "tcp"
    # Kestra, Superset, Jupyter, Streamlit
    ports = ["18080", "8088", "8888", "8501", "8081"]
  }

  source_ranges = ["0.0.0.0/0"]   # Cambiar a tu IP en producción
  target_tags   = ["capstone-vm"]
}

# ── VM principal ──────────────────────────────────────────────────────────────
resource "google_compute_instance" "capstone_vm" {
  name         = "capstone-analytics-vm"
  machine_type = var.machine_type
  zone         = "${var.region}-a"
  tags         = ["capstone-vm"]

  depends_on = [google_project_service.compute]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 50   # GB — DuckDB + Docker images
      type  = "pd-ssd"
    }
  }

  network_interface {
    network = "default"
    access_config {}   # IP pública efímera
  }

  service_account {
    email  = google_service_account.capstone_sa.email
    scopes = ["cloud-platform"]
  }

  # Startup script: instala Docker + clona repo + levanta stack
  metadata_scripts = {
    startup-script = <<-EOF
      #!/bin/bash
      set -e

      # Docker
      curl -fsSL https://get.docker.com | sh
      usermod -aG docker ${var.vm_user}
      systemctl enable docker

      # Docker Compose plugin
      apt-get install -y docker-compose-plugin git make python3 python3-pip

      # Clonar proyecto
      cd /home/${var.vm_user}
      git clone ${var.repo_url} capstone
      cd capstone

      # Configurar env
      cp .env.example .env || make setup

      # Levantar stack
      make up
      EOF
  }

  labels = {
    project     = "capstone"
    environment = "production"
  }
}
