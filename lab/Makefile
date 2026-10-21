# The front door for building and checking the lab. Run from the lab/ folder on admin01.
# Layers are added in build-guide order; `make help` lists what exists.
.PHONY: help lint guests baseline trust identity services
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

lint: ## Static checks: yamllint, shellcheck, Ansible syntax
	cd .. && yamllint -c lab/.yamllint lab
	cd .. && shellcheck $$(find lab scripts weeks -name '*.sh')
	cd ansible && for p in playbooks/*.yml; do ansible-playbook --syntax-check $$p || exit 1; done
