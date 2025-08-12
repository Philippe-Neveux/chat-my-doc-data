output "vm_name" {
  description = "Name of the VM instance"
  value       = google_compute_instance.qdrant_vm.name
}

output "vm_internal_ip" {
  description = "Internal IP address of the VM"
  value       = google_compute_instance.qdrant_vm.network_interface[0].network_ip
}

output "vm_external_ip" {
  description = "External IP address of the VM"
  value       = google_compute_instance.qdrant_vm.network_interface[0].access_config[0].nat_ip
}

output "static_ip_address" {
  description = "Static IP address (if enabled)"
  value       = var.use_static_ip ? google_compute_address.qdrant_static_ip[0].address : null
}

output "persistent_disk_name" {
  description = "Name of the persistent disk"
  value       = google_compute_disk.qdrant_data_disk.name
}

output "zone" {
  description = "Zone where resources are deployed"
  value       = var.zone
}