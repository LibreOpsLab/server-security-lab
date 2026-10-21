from pathlib import Path

import pytest

jinja2 = pytest.importorskip("jinja2")
yaml = pytest.importorskip("yaml")

LAB = Path(__file__).parents[2] / "lab"
ROLE = LAB / "ansible/roles/authelia"
VARS = yaml.safe_load((LAB / "inventory/group_vars/all.yml").read_text())

SECRET_MARK = "SECRET-FROM-FILE"


def render():
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(ROLE / "templates"), undefined=jinja2.StrictUndefined)
    env.globals["lookup"] = lambda *a, **k: SECRET_MARK
    variables = {**VARS, "lab_secrets_dir": "/s", "authelia_session_domain": VARS["lab_domain"]}
    # defaults/main.yml supplies the role's own variables
    variables.update(yaml.safe_load((ROLE / "defaults/main.yml").read_text()))
    text = env.get_template("configuration.yml.j2").render(**variables)
    return text, yaml.safe_load(text)


def test_renders_valid_yaml():
    _, cfg = render()
    assert cfg["server"]["address"].startswith("tcp://")


def test_ldap_backend_points_at_samba_with_the_service_account():
    _, cfg = render()
    ldap = cfg["authentication_backend"]["ldap"]
    assert ldap["implementation"] == "activedirectory" and ldap["address"] == VARS["lab_ldap_uri"]
    assert ldap["base_dn"] == VARS["lab_base_dn"] and ldap["user"] == f"CN=svc-authelia,{VARS['lab_service_dn']}"
    assert ldap["additional_users_dn"] == "OU=LabUsers"


def test_totp_enabled_and_admins_need_two_factor():
    _, cfg = render()
    assert "totp" in cfg and cfg["totp"].get("disable") is not True
    rules = cfg["access_control"]["rules"]
    assert any(r.get("policy") == "two_factor" and "group:admins" in str(r.get("subject")) for r in rules)
    assert cfg["access_control"]["default_policy"] == "one_factor"  # the lab's relaxed default


def test_storage_is_sqlite_and_sessions_stay_in_memory():
    _, cfg = render()
    assert "local" in cfg["storage"] and "redis" not in cfg["session"]


def test_nextcloud_oidc_client_has_the_expected_redirect():
    _, cfg = render()
    client = next(c for c in cfg["identity_providers"]["oidc"]["clients"] if c["client_id"] == "nextcloud")
    assert "https://cloud.lab.internal/apps/oidc_login/oidc" in client["redirect_uris"]
    assert {"openid", "profile", "email", "groups"} <= set(client["scopes"])


def test_every_secret_comes_from_a_lookup_never_a_literal():
    text, _ = render()
    assert text.count(SECRET_MARK) >= 6  # jwt, session, storage key, hmac, ldap password, client secret, jwks key
    template = (ROLE / "templates/configuration.yml.j2").read_text()
    assert "lookup(" in template and "password: 'changeme" not in template


def test_session_cookie_covers_the_lab_domain_and_the_portal_url():
    _, cfg = render()
    cookie = cfg["session"]["cookies"][0]
    assert cookie["domain"] == "lab.internal" and cookie["authelia_url"] == "https://auth.lab.internal"


def test_package_is_installed_from_a_pinned_release_and_config_is_validated():
    tasks = (ROLE / "tasks/main.yml").read_text()
    assert "authelia_version" in tasks and "get_url" in tasks and "validate-config" in tasks
    assert "latest" not in tasks.lower().replace("latest news", "")


def test_services_playbook_builds_the_authelia_guest():
    assert "authelia" in (LAB / "ansible/playbooks/40-services.yml").read_text()
