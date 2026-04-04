# terraform/outputs.tf

output "vm_external_ip" {
  description = "IP pública de la VM"
  value       = google_compute_instance.capstone_vm.network_interface[0].access_config[0].nat_ip
}

output "stack_urls" {
  description = "URLs del stack una vez levantado"
  value = {
    kestra    = "http://${google_compute_instance.capstone_vm.network_interface[0].access_config[0].nat_ip}:18080"
    superset  = "http://${google_compute_instance.capstone_vm.network_interface[0].access_config[0].nat_ip}:8088"
    streamlit = "http://${google_compute_instance.capstone_vm.network_interface[0].access_config[0].nat_ip}:8501"
    jupyter   = "http://${google_compute_instance.capstone_vm.network_interface[0].access_config[0].nat_ip}:8888"
  }
}

output "gcs_bucket" {
  description = "GCS bucket para datos"
  value       = google_storage_bucket.capstone_data.name
}
