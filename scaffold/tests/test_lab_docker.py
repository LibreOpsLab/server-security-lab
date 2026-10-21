import re
import shutil
import subprocess
from pathlib import Path

import pytest

LAB = Path(__file__).parents[2] / "lab"
STACKS = ["traefik", "nextcloud", "stirling-pdf", "vaultwarden"]
ROLE = LAB / "ansible/roles/docker_host"


def compose(stack):
    return (LAB / "docker" / stack / "docker-compose.yml").read_text()


@pytest.mark.skipif(shutil.which("docker") is None, reason="docker not installed")
@pytest.mark.parametrize("stack", STACKS)
def test_compose_files_validate_with_the_example_env(stack):
    d = LAB / "docker" / stack
    r = subprocess.run(["docker", "compose", "--env-file", ".env.example", "config", "-q"], cwd=d, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("stack", STACKS)
def test_no_latest_image_tags_and_services_restart(stack):
    text = compose(stack)
    images = re.findall(r"^\s*image:\s*(\S+)", text, re.M)
    assert images and all(":" in i and not i.endswith(":latest") for i in images), images
    assert "restart: unless-stopped" in text


def test_apps_are_routed_by_traefik_on_the_expected_hostnames():
    assert "Host(`cloud.lab.internal`)" in compose("nextcloud")
    assert "Host(`pdf.lab.internal`)" in compose("stirling-pdf")
    assert "Host(`vault.lab.internal`)" in compose("vaultwarden")


def test_stirling_and_the_vault_web_ui_use_forward_auth_but_not_the_bitwarden_api_paths():
    assert "middlewares=authelia@file" in compose("stirling-pdf")
    vault = compose("vaultwarden")
    web = re.search(r"vaultwarden-web\.middlewares=(\S+)", vault)
    assert web and web.group(1) == "authelia@file"
    assert "vaultwarden-api.middlewares" not in vault and "PathPrefix(`/api`" in vault


def test_nextcloud_database_is_on_a_named_volume_not_a_bind_mount():
    assert "nextcloud_db:/var/lib/mysql" in compose("nextcloud")


def test_env_examples_contain_only_placeholders():
    for stack in STACKS:
        for ln in (LAB / "docker" / stack / ".env.example").read_text().splitlines():
            if "=" in ln and not ln.startswith("#"):
                value = ln.split("=", 1)[1]
                assert value in ("CHANGE-ME", "/opt/lab/certs"), (stack, ln)


def test_traefik_routes_auth_and_grafana_and_has_the_authelia_middleware_but_no_security_headers():
    dyn = (ROLE / "templates/dynamic.yml.j2").read_text()
    assert "forwardAuth" in dyn and ":9091/api/authz/forward-auth" in dyn and "auth01" in dyn
    assert "auth.lab.internal" in dyn.replace("{{ lab_domain }}", "lab.internal") or "authelia_portal_host" in dyn
    assert "grafana" in dyn and "headers:" not in dyn.replace("authResponseHeaders", "")  # no header-hardening middleware


def test_nextcloud_oidc_settings_use_authelia_and_a_variable_secret():
    php = (ROLE / "templates/oidc.config.php.j2").read_text()
    assert "oidc_login_provider_url" in php and "authelia_portal_host" in php  # the sign-in portal is the provider
    assert "authelia_oidc_nextcloud_secret" in php and "oidc_login_client_id' => 'nextcloud'" in php
    assert "default_certificates_bundle_path" in php and "ca-certificates.crt" in php


def test_role_renders_env_files_from_secrets_privately():
    tasks = (ROLE / "tasks/main.yml").read_text()
    assert "nextcloud_db_password" in tasks and "vaultwarden_admin_token" in tasks
    assert re.search(r"\.env", tasks) and 'mode: "0600"' in tasks and "no_log: true" in tasks


def test_apps_playbook_installs_docker_from_the_distribution_not_an_unchecked_script():
    tasks = (ROLE / "tasks/main.yml").read_text()
    assert "docker.io" in tasks and "get.docker.com" not in tasks
    assert "docker_host" in (LAB / "ansible/playbooks/50-apps.yml").read_text()


def test_oidc_config_with_the_client_secret_is_not_world_readable():
    tasks = (ROLE / "tasks/main.yml").read_text()
    block = tasks.split("Write NextCloud's single sign-on settings")[1].split("- name:")[0]
    assert 'mode: "0640"' in block and 'group: "33"' in block  # readable by NextCloud's www-data only


def test_nextcloud_database_root_password_is_its_own_secret_not_derived():
    tasks = (ROLE / "tasks/main.yml").read_text()
    assert "nextcloud_db_root_password" in tasks and "hash(" not in tasks
    assert "nextcloud_db_root_password" in (LAB.parent / "scripts/gen-secrets.sh").read_text()


def test_vaultwarden_does_not_allow_open_signups():
    assert 'SIGNUPS_ALLOWED: "false"' in compose("vaultwarden")
    assert 'INVITATIONS_ALLOWED: "true"' in compose("vaultwarden")


def test_nextcloud_trusts_only_the_pinned_proxy_network():
    assert "TRUSTED_PROXIES: 172.30.0.0/24" in compose("nextcloud")
    assert "172.30.0.0/24" in compose("traefik") and "172.16.0.0/12" not in compose("nextcloud")


def test_docker_socket_mount_is_documented_as_a_deliberate_weak_default():
    assert "docker.sock" in compose("traefik") and "deliberate" in compose("traefik").lower()


def test_vaultwarden_alive_healthcheck_bypasses_sso_like_the_rest_of_the_api():
    # /alive is Vaultwarden's own liveness endpoint; it was missing from the unauthenticated router's
    # path list, so it went through the SSO router and returned a redirect instead of a health status.
    assert "PathPrefix(`/api`,`/identity`,`/notifications`,`/events`,`/alive`)" in compose("vaultwarden")


def test_nextcloud_mounts_the_lab_ca_over_the_containers_own_system_bundle():
    # oidc_login (Jumbojett) makes its own HTTP calls to the OIDC provider using the container's default
    # system CA bundle, not NextCloud's own 'default_certificates_bundle_path' setting (that only affects
    # NextCloud's own HTTP client). The host bundle (with the lab CA trusted via make trust) must replace
    # the container's own bundle at its real path for OIDC discovery to pass TLS verification.
    nc = compose("nextcloud")
    assert "/etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro" in nc
