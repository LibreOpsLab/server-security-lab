"""scripts/set-domain.py: change the lab domain everywhere from one value."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parents[2]
SCRIPT = REPO / "scripts" / "set-domain.py"


@pytest.fixture
def copy(tmp_path):
    ignore = shutil.ignore_patterns("node_modules", ".git", "secrets", "__pycache__", "_site")
    for part in ("lab", "docs", "weeks", "scripts"):
        shutil.copytree(REPO / part, tmp_path / part, ignore=ignore)
    for f in ("README.md", "CHANGELOG.md"):
        shutil.copy(REPO / f, tmp_path / f)
    return tmp_path


def run(root, *args, env_file=None):
    cmd = [sys.executable, str(SCRIPT), "--root", str(root), *args]
    if env_file:
        cmd += ["--env", str(env_file)]
    return subprocess.run(cmd, capture_output=True, text=True)


def read(root, rel):
    return (root / rel).read_text(encoding="utf-8")


def test_dry_run_changes_nothing(copy):
    before = read(copy, "lab/inventory/group_vars/all.yml")
    r = run(copy, "--domain", "acme.example.org")
    assert r.returncode == 0 and "would change" in r.stdout and "Dry run" in r.stdout
    assert read(copy, "lab/inventory/group_vars/all.yml") == before


def test_apply_rewrites_every_spelling_in_the_inventory(copy):
    r = run(copy, "--domain", "acme.example.org", "--apply")
    assert r.returncode == 0, r.stderr
    text = read(copy, "lab/inventory/group_vars/all.yml")
    assert "lab_domain: acme.example.org" in text and "lab_realm: ACME.EXAMPLE.ORG" in text
    assert "lab_netbios: ACME" in text
    assert "lab_base_dn: DC=acme,DC=example,DC=org" in text
    assert "lab_users_dn: OU=LabUsers,DC=acme,DC=example,DC=org" in text
    assert "lab_ldap_uri: ldaps://samba-dc01.acme.example.org" in text
    assert "mail01.acme.example.org" in text and "info@acme.example.org" in text


def test_no_old_domain_is_left_in_lab_and_it_is_idempotent(copy):
    run(copy, "--domain", "acme.example.org", "--apply")
    left = [
        p.relative_to(copy).as_posix()
        for p in (copy / "lab").rglob("*")
        if p.is_file() and "boab.lab" in p.read_text(encoding="utf-8", errors="ignore").lower()
    ]
    assert left == []
    again = run(copy, "--domain", "acme.example.org", "--apply")
    assert "Nothing to change" in again.stdout


def test_changelog_and_tests_are_never_touched(copy):
    before = read(copy, "CHANGELOG.md")
    run(copy, "--domain", "acme.example.org", "--docs", "--apply")
    assert read(copy, "CHANGELOG.md") == before


def test_docs_are_only_rewritten_with_the_flag(copy):
    run(copy, "--domain", "acme.example.org", "--apply")
    assert "boab.lab" in read(copy, "docs/build/10-docker-vm-and-apps.md")
    run(copy, "--domain", "acme.example.org", "--docs", "--apply")  # inventory already changed: nothing to do
    # a fresh copy with the flag changes the guides and the sign-in name
    other = copy.parent / "other"
    other.mkdir()
    for part in ("lab", "docs", "weeks", "scripts"):
        shutil.copytree(REPO / part, other / part, ignore=shutil.ignore_patterns("node_modules", ".git", "secrets", "__pycache__", "_site"))
    run(other, "--domain", "acme.example.org", "--docs", "--apply")
    assert "boab.lab" not in read(other, "docs/build/10-docker-vm-and-apps.md")
    assert "ACME" + "\\alice" in read(other, "docs/build/17-windows-11-optional.md")


def test_domain_comes_from_the_env_file(copy, tmp_path):
    env = tmp_path / "my.env"
    env.write_text("# comment\nLAB_DOMAIN='corp.test'\nLAB_NETBIOS=CORP1\n")
    r = run(copy, "--apply", env_file=env)
    assert r.returncode == 0, r.stderr
    text = read(copy, "lab/inventory/group_vars/all.yml")
    assert "lab_domain: corp.test" in text and "lab_netbios: CORP1" in text


def test_a_new_domain_that_contains_the_old_one_is_not_rewritten_twice(copy):
    run(copy, "--domain", "dev.boab.lab", "--apply")
    text = read(copy, "lab/inventory/group_vars/all.yml")
    assert "lab_domain: dev.boab.lab" in text and "dev.dev" not in text and "DEV.DEV" not in text
    assert "lab_realm: DEV.BOAB.LAB" in text


@pytest.mark.parametrize("bad", ["Boab Lab", "nodots", "-bad.lab", "a..b", "x.lab; rm -rf /", ""])
def test_bad_domains_are_refused_and_nothing_changes(copy, bad):
    before = read(copy, "lab/inventory/group_vars/all.yml")
    r = run(copy, "--domain", bad, "--apply")
    assert r.returncode != 0
    assert read(copy, "lab/inventory/group_vars/all.yml") == before


def test_bad_netbios_is_refused(copy):
    assert run(copy, "--domain", "acme.test", "--netbios", "THIS-NAME-IS-WAY-TOO-LONG", "--apply").returncode != 0
