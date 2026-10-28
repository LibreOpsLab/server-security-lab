# The front door for building and checking the lab. Run from the lab/ folder on admin01.
# Layers are added in build-guide order; `make help` lists what exists.
.PHONY: help lint preflight evidence backup-dc guests baseline trust identity services files mail sso radius apps monitoring backup verify
help:
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

preflight: ## Check a stage is ready before you run it: make preflight STAGE=identity (STAGE=debian-vm HOST=pbs01)
	./preflight.sh $(STAGE) $(HOST)

evidence: ## Collect command-line evidence for a guide: make evidence GUIDE=07
	./evidence.sh $(GUIDE)

guests: ## Create the LXC containers and the Docker VM on Proxmox
	cd ansible && ansible-playbook playbooks/10-guests.yml

baseline: ## Give guests the functional baseline (time, SSH, exporter). LIMIT=host for one machine
	cd ansible && ansible-playbook playbooks/20-baseline.yml --limit '$(or $(LIMIT),lxc:vm:admin)'

trust: ## Make guests trust the lab CA (LIMIT=host for one machine; pbs01 is added in guide 16)
	cd ansible && ansible-playbook playbooks/25-trust.yml --limit '$(or $(LIMIT),all:!pbs01)'

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

monitoring: ## Build Prometheus, Grafana, Loki and ship guests' logs (LIMIT=host for one machine)
	cd ansible && ansible-playbook playbooks/60-monitoring.yml --limit '$(or $(LIMIT),all:!pbs01)'

backup: ## Build the backup server and the nightly job
	cd ansible && ansible-playbook playbooks/70-backup.yml

backup-dc: ## Back up the domain controller (a VMware VM, so Proxmox's job cannot)
	./backup-dc.sh

verify: ## Smoke-test every service (PASS, FAIL or SKIP per check)
	./verify/verify.sh

lint: ## Static checks: yamllint, shellcheck, Ansible syntax
	cd .. && yamllint -c lab/.yamllint lab
	cd .. && shellcheck $$(find lab scripts weeks -name '*.sh')
	cd ansible && for p in playbooks/*.yml; do ansible-playbook --syntax-check $$p || exit 1; done
