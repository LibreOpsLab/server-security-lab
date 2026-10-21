# The front door for building and checking the lab. Run from the lab/ folder on admin01.
# Layers are added in build-guide order; `make help` lists what exists.
.PHONY: help lint
help:
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

lint: ## Static checks: yamllint, shellcheck, Ansible syntax
	cd .. && yamllint -c lab/.yamllint lab
	cd .. && shellcheck $$(find lab scripts weeks -name '*.sh')
	cd ansible && for p in playbooks/*.yml; do ansible-playbook --syntax-check $$p || exit 1; done
