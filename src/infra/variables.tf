variable "project_id" {
  description = "ID of the GCP project"
  type        = string
  default     = "gen-ai-466406"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "australia-southeast1"
}

variable "zone" {
  description = "The GCP zone"
  type        = string
  default     = "australia-southeast1-b"
}

variable "machine_type" {
  description = "The machine type for the VM"
  type        = string
  default     = "e2-medium"
}

variable "disk_size_gb" {
  description = "Size of the persistent disk in GB"
  type        = number
  default     = 20
}

variable "boot_disk_size_gb" {
  description = "Size of the boot disk in GB"
  type        = number
  default     = 20
}

variable "boot_disk_image" {
  description = "The boot disk image"
  type        = string
  default     = "ubuntu-os-cloud/ubuntu-2204-lts"
}

variable "ssh_user" {
  description = "SSH user for the VM"
  type        = string
  default     = "ubuntu"
}

variable "environment" {
  description = "Environment label"
  type        = string
  default     = "production"
}

variable "allowed_source_ranges" {
  description = "List of CIDR blocks allowed to access Qdrant"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "use_static_ip" {
  description = "Whether to use a static external IP address"
  type        = bool
  default     = true
}