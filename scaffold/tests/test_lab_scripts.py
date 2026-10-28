import shutil
import subprocess
from pathlib import Path

import pytest

LAB = Path(__file__).parents[2] / "lab"
SCRIPTS = [LAB / "bootstrap" / "prep-guest.sh", LAB / "preflight.sh", LAB / "evidence.sh", LAB / "backup-dc.sh"]

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="needs bash")


def run(script, *args):
    return subprocess.run(["bash", str(script), *args], capture_output=True, text=True, timeout=30)


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.name)
def test_script_is_valid_bash_with_lf_endings(script):
    assert b"\r" not in script.read_bytes()
    assert subprocess.run(["bash", "-n", str(script)], capture_output=True).returncode == 0


def test_prep_guest_refuses_to_run_without_root_or_with_a_private_key():
    # Not root in the test run, or bad arguments: either way it must exit 2 and change nothing.
    r = run(LAB / "bootstrap" / "prep-guest.sh", "samba-dc01", "-----BEGIN OPENSSH PRIVATE KEY-----")
    assert r.returncode == 2


def test_preflight_rejects_an_unknown_stage():
    r = run(LAB / "preflight.sh", "nonsense")
    assert r.returncode == 2 and "usage" in r.stderr


def test_evidence_rejects_a_bad_or_unknown_guide_number():
    assert run(LAB / "evidence.sh", "x").returncode == 2
    assert run(LAB / "evidence.sh", "99").returncode == 2


def test_makefile_has_the_preflight_and_evidence_targets():
    makefile = (LAB / "Makefile").read_text()
    assert "preflight:" in makefile and "evidence:" in makefile


def test_evidence_script_never_prints_the_contents_of_secrets():
    text = (LAB / "evidence.sh").read_text()
    assert "cat " not in text and "secrets/ca/root/private" not in text
