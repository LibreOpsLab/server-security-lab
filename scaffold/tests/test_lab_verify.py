import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parents[2]
VERIFY = REPO / "lab" / "verify" / "verify.sh"
CHECKS = REPO / "lab" / "verify" / "checks"
LIB = REPO / "lab" / "verify" / "lib.sh"


def make_checks(tmp_path, **lines):
    d = tmp_path / "checks"
    d.mkdir()
    for i, (name, body) in enumerate(lines.items(), 1):
        f = d / f"{i:02d}-{name}.sh"
        f.write_text(f"#!/usr/bin/env bash\n{body}\n")
        f.chmod(0o755)
    return d


def run(checks_dir, *args, timeout="5"):
    env = {**os.environ, "VERIFY_CHECKS_DIR": str(checks_dir), "VERIFY_TIMEOUT": timeout}
    return subprocess.run([str(VERIFY), *args], env=env, capture_output=True, text=True)


def test_all_pass_exits_0_and_prints_a_summary(tmp_path):
    d = make_checks(tmp_path, dns='echo "PASS dns resolves"', ntp='echo "PASS ntp synced"')
    r = run(d)
    assert r.returncode == 0 and "2 passed, 0 failed, 0 skipped" in r.stdout


def test_any_fail_exits_1(tmp_path):
    d = make_checks(tmp_path, dns='echo "PASS dns ok"', mail='echo "FAIL mail port closed"')
    r = run(d)
    assert r.returncode == 1 and "1 passed, 1 failed, 0 skipped" in r.stdout and "FAIL mail" in r.stdout


def test_a_skipped_optional_check_is_not_a_failure(tmp_path):
    d = make_checks(tmp_path, dns='echo "PASS dns ok"', windows='echo "SKIP windows not built"')
    r = run(d)
    assert r.returncode == 0 and "1 skipped" in r.stdout


def test_only_flag_runs_a_single_check(tmp_path):
    d = make_checks(tmp_path, dns='echo "PASS dns ok"', mail='echo "FAIL mail closed"')
    r = run(d, "--only", "dns")
    assert r.returncode == 0 and "1 passed, 0 failed, 0 skipped" in r.stdout and "mail" not in r.stdout


def test_unknown_only_name_is_an_error(tmp_path):
    d = make_checks(tmp_path, dns='echo "PASS dns ok"')
    assert run(d, "--only", "nope").returncode == 2


@pytest.mark.parametrize("body", ["true", 'echo "PASS a ok"; echo "PASS b ok"', 'echo "garbage"', "exit 3"])
def test_a_check_that_does_not_print_exactly_one_status_line_counts_as_a_failure(tmp_path, body):
    d = make_checks(tmp_path, odd=body)
    r = run(d)
    assert r.returncode == 1 and "FAIL" in r.stdout


def test_a_hanging_check_is_cut_off_and_fails(tmp_path):
    d = make_checks(tmp_path, slow="sleep 30")
    r = run(d, timeout="1")
    assert r.returncode == 1 and "timed out" in r.stdout


def test_lib_reads_addresses_from_the_inventory_not_a_copy():
    out = subprocess.run(["bash", "-c", f'source "{LIB}"; lab_ip samba-dc01; lab_ip win-client01; lab_var lab_domain'],
                         capture_output=True, text=True, env={**os.environ, "VERIFY_ROOT": str(REPO)})
    assert out.stdout.split() == ["10.10.10.21", "10.10.10.11", "lab.internal"]


def test_every_real_check_prints_one_status_line_and_never_crashes_without_the_tools(tmp_path):
    checks = sorted(CHECKS.glob("*.sh"))
    assert len(checks) >= 17
    # A PATH with the basic utilities but none of the lab tools (curl, dig, nc, smbclient, ...).
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in ("bash", "sed", "head", "basename", "dirname", "grep", "awk", "sort", "cat", "mktemp", "rm", "chmod"):
        src = shutil.which(tool)
        assert src, tool
        (bin_dir / tool).symlink_to(src)
    for c in checks:
        r = subprocess.run([str(bin_dir / "bash"), str(c)], capture_output=True, text=True,
                           env={"PATH": str(bin_dir), "VERIFY_ROOT": str(REPO)})
        lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
        assert r.returncode == 0 and len(lines) == 1 and re.match(r"(PASS|FAIL|SKIP) \S+ ", lines[0]), (c.name, r.stdout, r.stderr)


def test_the_five_weak_defaults_are_all_checked_by_name():
    text = (CHECKS / "20-weak-defaults.sh").read_text()
    for needle in ("VRFY", "smbclient", "Strict-Transport-Security", "PasswordAuthentication", "enum"):
        assert needle in text
