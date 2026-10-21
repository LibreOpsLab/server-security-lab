"""Static validation of everything under lab/: the only checks possible without a real Proxmox."""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parents[2]
LAB = REPO / "lab"
PLAYBOOKS = sorted((LAB / "ansible" / "playbooks").glob("*.yml"))


@pytest.mark.skipif(shutil.which("ansible-playbook") is None, reason="ansible not installed")
@pytest.mark.parametrize("playbook", PLAYBOOKS, ids=lambda p: p.name)
def test_playbook_passes_syntax_check(playbook):
    r = subprocess.run(["ansible-playbook", "--syntax-check", f"playbooks/{playbook.name}"],
                       cwd=LAB / "ansible", capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_there_is_at_least_one_playbook():
    assert PLAYBOOKS


@pytest.mark.skipif(shutil.which("yamllint") is None, reason="yamllint not installed")
def test_yamllint_clean():
    r = subprocess.run(["yamllint", "-c", str(LAB / ".yamllint"), str(LAB)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


@pytest.mark.skipif(shutil.which("shellcheck") is None, reason="shellcheck not installed")
def test_shellcheck_clean():
    scripts = [str(p) for p in [*LAB.rglob("*.sh"), *(REPO / "scripts").glob("*.sh"), *REPO.glob("weeks/*/check.sh")]]
    r = subprocess.run(["shellcheck", *scripts], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


@pytest.mark.skipif(shutil.which("ansible-lint") is None, reason="ansible-lint not installed")
def test_ansible_lint_clean():
    r = subprocess.run(["ansible-lint", "-q", "--offline", "playbooks", "roles"], cwd=LAB / "ansible", capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr[-800:]


def test_ansible_cfg_uses_a_callback_both_pip_and_pipx_ansible_ship():
    cfg = (LAB / "ansible" / "ansible.cfg").read_text()
    assert "stdout_callback = default" in cfg or "stdout_callback = yaml" not in cfg
