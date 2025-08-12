# Qdrant Ansible Playbooks

This directory contains Ansible playbooks for deploying and managing Qdrant vector database.

## Prerequisites

1. Ansible installed (>= 2.9)
2. SSH access to the target VM
3. VM deployed using the Terraform configuration

## Setup

1. Update the inventory file with your VM's IP address:
   ```yaml
   # inventory.yml
   all:
     children:
       qdrant:
         hosts:
           qdrant-vm:
             ansible_host: "YOUR_VM_EXTERNAL_IP"
   ```

2. Test connectivity:
   ```bash
   ansible all -m ping
   ```

## Available Playbooks

### 1. Deploy Qdrant (`deploy-qdrant.yml`)

Installs and configures Qdrant on the target VM.

```bash
ansible-playbook deploy-qdrant.yml
```

This playbook:
- Installs required system packages
- Creates qdrant user and directories
- Downloads and installs Qdrant binary
- Configures Qdrant service
- Starts and enables the service

### 2. Manage Qdrant (`manage-qdrant.yml`)

Provides management and monitoring capabilities.

```bash
ansible-playbook manage-qdrant.yml
```

This playbook:
- Checks service status
- Shows version information
- Lists collections
- Displays disk usage
- Shows recent logs

### 3. Backup Qdrant (`backup-qdrant.yml`)

Creates backups of Qdrant data.

```bash
ansible-playbook backup-qdrant.yml
```

Optional: Backup specific collection
```bash
ansible-playbook backup-qdrant.yml -e collection_name=my_collection
```

## Configuration

The Qdrant configuration is templated in `templates/qdrant-config.yaml.j2`. Key settings:

- **Storage Path**: `/opt/qdrant/data` (persistent disk mount point)
- **HTTP Port**: 6333
- **gRPC Port**: 6334
- **CORS**: Enabled
- **Clustering**: Disabled (single-node setup)

## Service Management

Qdrant runs as a systemd service. Common commands:

```bash
# Check status
sudo systemctl status qdrant

# Start service
sudo systemctl start qdrant

# Stop service
sudo systemctl stop qdrant

# Restart service
sudo systemctl restart qdrant

# View logs
sudo journalctl -u qdrant -f
```

## API Access

Once deployed, Qdrant API is available at:
- REST API: `http://VM_IP:6333`
- Web UI: `http://VM_IP:6333/dashboard`
- Health check: `http://VM_IP:6333/health`

## Troubleshooting

1. **Service won't start**: Check logs with `journalctl -u qdrant -f`
2. **Port not accessible**: Verify firewall rules and GCP network settings
3. **Data persistence issues**: Ensure persistent disk is properly mounted
4. **Performance issues**: Monitor disk I/O and consider upgrading machine type