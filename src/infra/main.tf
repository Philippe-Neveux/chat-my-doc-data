terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_address" "qdrant_static_ip" {
  count  = var.use_static_ip ? 1 : 0
  name   = "qdrant-static-ip"
  region = var.region
}

resource "google_compute_disk" "qdrant_data_disk" {
  name = "qdrant-data-disk"
  type = "pd-ssd"
  zone = var.zone
  size = var.disk_size_gb

  labels = {
    environment = var.environment
    service     = "qdrant"
  }
}

resource "google_compute_instance" "qdrant_vm" {
  name         = "qdrant-vm"
  machine_type = var.machine_type
  zone         = var.zone

  tags = ["qdrant", "vector-db"]

  boot_disk {
    initialize_params {
      image = var.boot_disk_image
      size  = var.boot_disk_size_gb
      type  = "pd-standard"
    }
  }

  attached_disk {
    source      = google_compute_disk.qdrant_data_disk.id
    device_name = "qdrant-data"
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = var.use_static_ip ? google_compute_address.qdrant_static_ip[0].address : null
    }
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    # Format and mount the persistent disk
    if ! blkid /dev/disk/by-id/google-qdrant-data; then
      mkfs.ext4 -F /dev/disk/by-id/google-qdrant-data
    fi
    
    mkdir -p /opt/qdrant/data
    mount /dev/disk/by-id/google-qdrant-data /opt/qdrant/data
    echo '/dev/disk/by-id/google-qdrant-data /opt/qdrant/data ext4 defaults 0 2' >> /etc/fstab
    
    # Set proper permissions
    chown -R 1000:1000 /opt/qdrant/data
  EOF

  service_account {
    scopes = ["cloud-platform"]
  }

  labels = {
    environment = var.environment
    service     = "qdrant"
  }
}

resource "google_compute_firewall" "qdrant_firewall" {
  name    = "qdrant-firewall"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["6333", "6334"]
  }

  source_ranges = var.allowed_source_ranges
  target_tags   = ["qdrant"]
}