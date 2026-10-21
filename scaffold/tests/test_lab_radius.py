import re
from pathlib import Path

import pytest

jinja2 = pytest.importorskip("jinja2")
yaml = pytest.importorskip("yaml")

LAB = Path(__file__).parents[2] / "lab"
ROLE = LAB / "ansible/roles/radius"
VARS = yaml.safe_load((LAB / "inventory/group_vars/all.yml").read_text())


def code(path):
    return "\n".join(ln for ln in path.read_text().splitlines() if not ln.strip().startswith("#"))


def test_clients_conf_takes_its_secret_from_the_generated_file():
    text = code(ROLE / "templates/clients.conf.j2")
    assert "radius_shared_secret" in text and "testing123" not in text
    assert "{{ lab_subnet }}" in text


def test_mschap_uses_ntlm_auth_and_limits_logins_to_the_wifi_group():
    text = code(ROLE / "templates/mschap.j2")
    assert "--request-nt-key" in text and "ntlm_auth" in text
    assert re.search(r"--require-membership-of=\{\{ lab_netbios \}\}\\\\+wifi", text)


def test_eap_defaults_to_peap_with_the_lab_certificate():
    tasks = (ROLE / "tasks/main.yml").read_text()
    assert "default_eap_type" in tasks and "peap" in tasks
    assert "radius01.{{ lab_domain }}" in tasks or "radius_cert_cn" in tasks
    assert "private_key_file" in tasks and "certificate_file" in tasks


def test_freeradius_can_reach_winbind():
    tasks = (ROLE / "tasks/main.yml").read_text()
    assert "winbindd_priv" in tasks and "freerad" in tasks


def test_eapol_test_template_is_peap_mschapv2_with_no_real_password():
    tpl = (ROLE / "templates/eapol_test.conf.j2").read_text()
    assert 'eap=PEAP' in tpl and 'phase2="auth=MSCHAPV2"' in tpl and "lab-root-ca.crt" in tpl
    assert 'password="CHANGE-ME"' in tpl


def test_domain_join_is_shared_and_radius_is_built_by_the_services_playbook():
    assert "domain_join" in (ROLE / "tasks/main.yml").read_text()
    assert "role: radius" in (LAB / "ansible/playbooks/40-services.yml").read_text().replace("- radius", "role: radius") or "radius" in (LAB / "ansible/playbooks/40-services.yml").read_text()


def test_default_eap_type_edit_targets_the_first_match_not_the_last():
    # Ansible's lineinfile replaces the LAST matching line by default. FreeRADIUS's real eap file has
    # default_eap_type at the top level AND again inside the nested peap{} block; without firstmatch,
    # this edit would silently land on the wrong (inner) one.
    import yaml

    tasks = yaml.safe_load((LAB / "ansible/roles/radius/tasks/main.yml").read_text())
    task = next(t for t in tasks if "ansible.builtin.lineinfile" in t
                and any(isinstance(i, dict) and "default_eap_type" in str(i.get("regexp", "")) for i in t["loop"]))
    assert task["ansible.builtin.lineinfile"].get("firstmatch") is True, \
        "add firstmatch: true, or lineinfile edits the peap{} inner line"
