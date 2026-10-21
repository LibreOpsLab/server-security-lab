"""The weak-defaults register: the lab must be functional but NOT hardened (docs/design/lab-build-design.md).

The security loop needs something to find. These tests fail if hardening creeps into the build, and later
tasks add the positive checks (what must be left weak) beside the negative ones.
"""

import re
from pathlib import Path

import pytest

LAB = Path(__file__).parents[2] / "lab"

# (pattern, why it is forbidden). Matched against non-comment lines of files under lab/.
FORBIDDEN = [
    (r"PasswordAuthentication\s+no", "SSH password login must stay on (ssh-weak-creds)"),
    (r"PermitRootLogin\s+no\b", "root login is not blocked in the lab's default state"),
    (r"ufw\s+default\s+deny|policy:\s*deny|default:\s*deny", "no default-deny host firewall in the default build"),
    (r"disable_vrfy_command\s*=\s*yes", "Postfix VRFY stays on (mail-basics)"),
    (r"Strict-Transport-Security|stsSeconds|HSTS", "no HSTS on the web tier (web-basics)"),
    (r"unattended-upgrades", "no automatic updates in the default build (week 15 adds patching)"),
    (r"fail2ban", "no brute-force protection in the default build (week 15 adds it)"),
]
TEXT_SUFFIXES = {".yml", ".yaml", ".j2", ".conf", ".cnf", ".sh", ".cfg", ".ini", ".env", ".toml", ".json", ".xml"}


def lab_files():
    return [p for p in LAB.rglob("*") if p.is_file() and p.suffix in TEXT_SUFFIXES and "secrets" not in p.parts]


def code_lines(path):
    for i, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
        stripped = line.strip()
        if stripped and not stripped.startswith(("#", ";", "//")):
            yield i, line


@pytest.mark.parametrize("pattern,why", FORBIDDEN, ids=lambda x: x if isinstance(x, str) and len(x) < 30 else None)
def test_no_hardening_in_lab(pattern, why):
    hits = [f"{p.relative_to(LAB)}:{i}" for p in lab_files() for i, line in code_lines(p) if re.search(pattern, line, re.I)]
    assert not hits, f"{why}: {hits}"


def test_ssh_password_auth_explicitly_on():
    dropin = LAB / "ansible/roles/baseline/templates/10-lab.conf.j2"
    assert any(re.fullmatch(r"PasswordAuthentication\s+yes", line.strip()) for _, line in code_lines(dropin))


def test_python_is_bootstrapped_before_facts_are_gathered():
    text = (LAB / "ansible/playbooks/20-baseline.yml").read_text()
    assert "ansible.builtin.raw" in text and "python3" in text and "gather_facts: false" in text


def test_chrony_uses_the_domain_controller_for_everyone_else():
    tpl = (LAB / "ansible/roles/baseline/templates/chrony.conf.j2").read_text()
    assert "lab_hosts['samba-dc01'].ip" in tpl and "ntpsigndsocket" in tpl


def test_node_exporter_installed_and_enabled():
    tasks = (LAB / "ansible/roles/baseline/tasks/main.yml").read_text()
    assert "prometheus-node-exporter" in tasks and "enabled: true" in tasks
