# Qdrant Infrastructure on Google Cloud Platform

This directory contains Terraform configuration files to deploy a Qdrant vector database on Google Cloud Platform.

## Prerequisites

1. Google Cloud SDK installed and configured
2. Terraform installed (>= 1.0)
3. SSH key pair generated

## Quick Start

1. Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` with your project details:
   ```hcl
   project_id = "your-gcp-project-id"
   region     = "us-central1"
   zone       = "us-central1-a"
   # ... other variables
   ```

3. Initialize Terraform:
   ```bash
   terraform init
   ```

4. Plan the deployment:
   ```bash
   terraform plan
   ```

5. Apply the configuration:
   ```bash
   terraform apply
   ```

## Resources Created

- **Compute Instance**: VM running Ubuntu 22.04 LTS
- **Persistent Disk**: SSD disk for Qdrant data storage
- **Firewall Rules**: Allow access to Qdrant ports (6333, 6334)

## Outputs

After deployment, you'll get:
- VM external IP address
- VM internal IP address
- Persistent disk name

## Security Considerations

- Restrict `allowed_source_ranges` to your specific IP ranges
- Use private networks when possible
- Regularly update the VM and Qdrant software
- Consider using Cloud IAM for authentication

## Cleanup

To destroy the infrastructure:
```bash
terraform destroy
```