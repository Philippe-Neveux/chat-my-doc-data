data:
	uv run python src/chat_my_doc_app/main.py process-imdb-data

test:
	uv run pytest -v --cov=src --cov-report=html --cov-report=term

ruff:
	uv run ruff check src --fix --select I

mypy:
	uv run mypy src

# Terraform commands
tf-init:
	cd src/infra && terraform init

tf-plan: tf-init
	cd src/infra && terraform plan -out tfplan

tf-apply:
	cd src/infra && terraform apply tfplan

tf-apply-auto:
	cd src/infra && terraform apply -auto-approve

tf-destroy:
	cd src/infra && terraform destroy

tf-destroy-auto:
	cd src/infra && terraform destroy -auto-approve

tf-output:
	cd src/infra && terraform output

tf-validate:
	cd src/infra && terraform validate

tf-fmt:
	cd src/infra && terraform fmt

# Ansible commands
ansible-requirements:
	cd src/ansible_qdrant && uv run ansible-galaxy collection install -r requirements.yml

ansible-ping:
	cd src/ansible_qdrant && uv run ansible all -m ping

ansible-deploy:
	cd src/ansible_qdrant && uv run ansible-playbook deploy-qdrant.yml

ansible-manage:
	cd src/ansible_qdrant && uv run ansible-playbook manage-qdrant.yml

ansible-backup:
	cd src/ansible_qdrant && uv run ansible-playbook backup-qdrant.yml

ansible-syntax:
	cd src/ansible_qdrant && uv run ansible-playbook --syntax-check deploy-qdrant.yml

# Combined deployment workflow
deploy-infra: tf-init tf-plan tf-apply tf-output

deploy-qdrant: ansible-requirements ansible-ping ansible-deploy

deploy-all: deploy-infra
	@echo "Infrastructure deployed. Update src/ansible_qdrant/inventory.yml with VM IP from terraform output, then run 'make deploy-qdrant'"

# Cleanup
cleanup: tf-destroy-auto

# Help target
help:
	@echo "Available targets:"
	@echo "  Terraform:"
	@echo "    tf-init          - Initialize Terraform"
	@echo "    tf-plan          - Plan Terraform changes"
	@echo "    tf-apply         - Apply Terraform changes"
	@echo "    tf-apply-auto    - Apply changes without confirmation"
	@echo "    tf-destroy       - Destroy infrastructure"
	@echo "    tf-destroy-auto  - Destroy without confirmation"
	@echo "    tf-output        - Show Terraform outputs"
	@echo "    tf-validate      - Validate Terraform configuration"
	@echo "    tf-fmt           - Format Terraform files"
	@echo ""
	@echo "  Ansible:"
	@echo "    ansible-requirements - Install required Ansible collections"
	@echo "    ansible-ping        - Test connectivity to hosts"
	@echo "    ansible-deploy      - Deploy Qdrant"
	@echo "    ansible-manage      - Manage and monitor Qdrant"
	@echo "    ansible-backup      - Backup Qdrant data"
	@echo "    ansible-syntax      - Check playbook syntax"
	@echo ""
	@echo "  Combined:"
	@echo "    deploy-infra     - Deploy infrastructure (init, plan, apply)"
	@echo "    deploy-qdrant    - Deploy Qdrant application"
	@echo "    deploy-all       - Deploy everything (infrastructure first)"
	@echo "    cleanup          - Destroy all infrastructure"
	@echo "    help             - Show this help message"