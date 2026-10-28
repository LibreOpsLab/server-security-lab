# The front door for building and checking the lab. Run from the lab/ folder on admin01.
# Layers are added in build-guide order; `make help` lists what exists.
.PHONY: help lint guests baseline trust identity services files mail sso radius apps monitoring backup verify
help:
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

guests: ## Create the LXC containers and the Docker VM on Proxmox
	cd ansible && ansible-playbook playbooks/10-guests.yml

baseline: ## Give every guest the functional baseline (time, SSH, exporter)
	cd ansible && ansible-playbook playbooks/20-baseline.yml

trust: ## Make every guest trust the lab CA
	cd ansible && ansible-playbook playbooks/25-trust.yml

identity: ## Build Samba AD, DNS records and the lab users
	cd ansible && ansible-playbook playbooks/30-identity.yml

services: ## Build the file server, SSO, mail and Wi-Fi authentication guests
	cd ansible && ansible-playbook playbooks/40-services.yml

files: ## Build only the file server and SFTP (files01)
	cd ansible && ansible-playbook playbooks/40-services.yml --tags files

mail: ## Build only the mail server (mail01)
	cd ansible && ansible-playbook playbooks/40-services.yml --tags mail

sso: ## Build only single sign-on (auth01)
	cd ansible && ansible-playbook playbooks/40-services.yml --tags sso

radius: ## Build only Wi-Fi authentication (radius01)
	cd ansible && ansible-playbook playbooks/40-services.yml --tags radius

apps: ## Deploy Traefik, NextCloud, Stirling PDF and Vaultwarden on the Docker VM
	cd ansible && ansible-playbook playbooks/50-apps.yml

monitoring: ## Build Prometheus, Grafana, Loki and ship every guest's logs
	cd ansible && ansible-playbook playbooks/60-monitoring.yml

backup: ## Build the backup server and the nightly job
	cd ansible && ansible-playbook playbooks/70-backup.yml

verify: ## Smoke-test every service (PASS, FAIL or SKIP per check)
	./verify/verify.sh

lint: ## Static checks: yamllint, shellcheck, Ansible syntax
	cd .. && yamllint -c lab/.yamllint lab
	cd .. && shellcheck $$(find lab scripts weeks -name '*.sh')
	cd ansible && for p in playbooks/*.yml; do ansible-playbook --syntax-check $$p || exit 1; done
