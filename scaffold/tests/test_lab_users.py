import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parents[2]
LOADER = REPO / "lab" / "data" / "load-users.sh"
CSV = REPO / "lab" / "data" / "users.csv"
HEADER = "username,display_name,groups,initial_password\n"

FAKE = """#!/usr/bin/env bash
echo "$*" >>"$LOG"
case "$1 $2" in
  "user show"|"group show"|"ou list") exit 1 ;;
esac
exit 0
"""


@pytest.fixture
def loader(tmp_path):
    fake = tmp_path / "samba-tool"
    fake.write_text(FAKE)
    fake.chmod(0o755)
    env = {**os.environ, "SAMBA_TOOL": str(fake), "LOG": str(tmp_path / "log")}

    def run(csv_text=None, path=None):
        if csv_text is not None:
            path = tmp_path / "users.csv"
            path.write_text(csv_text)
        r = subprocess.run([str(LOADER), str(path)], env=env, capture_output=True, text=True)
        log = (tmp_path / "log").read_text() if (tmp_path / "log").exists() else ""
        return r, log

    return run


def test_valid_csv_creates_groups_then_users_then_memberships(loader):
    r, log = loader(HEADER + "alice,Alice Nguyen,staff;wifi,Welcome2026\nbob,Bob Tran,finance,Welcome2026\n")
    assert r.returncode == 0, r.stderr
    lines = log.splitlines()
    assert "group add staff" in lines and "group add wifi" in lines and "group add finance" in lines
    assert any(ln.startswith("user create alice Welcome2026") and "--given-name=Alice" in ln for ln in lines)
    assert "group addmembers staff alice" in lines and "group addmembers wifi alice" in lines
    first_user = next(i for i, ln in enumerate(lines) if ln.startswith("user create"))
    assert all(i < first_user for i, ln in enumerate(lines) if ln.startswith("group add "))


def test_existing_users_and_groups_are_skipped(tmp_path):
    fake = tmp_path / "samba-tool"
    fake.write_text('#!/usr/bin/env bash\necho "$*" >>"$LOG"\nexit 0\n')  # every `show` succeeds: all exist
    fake.chmod(0o755)
    csv = tmp_path / "u.csv"
    csv.write_text(HEADER + "alice,Alice Nguyen,staff,Welcome2026\n")
    env = {**os.environ, "SAMBA_TOOL": str(fake), "LOG": str(tmp_path / "log")}
    r = subprocess.run([str(LOADER), str(csv)], env=env, capture_output=True, text=True)
    assert r.returncode == 0
    log = (tmp_path / "log").read_text()
    assert "user create" not in log and "group add " not in log


@pytest.mark.parametrize("bad_username", ["bob; rm -rf /", "$(id)", "Alice", "a b", "x" * 40, "1abc", "../etc"])
def test_bad_username_rejected_before_any_call(loader, bad_username):
    r, log = loader(HEADER + f"{bad_username},Bob,staff,Welcome2026\n")
    assert r.returncode == 2 and log == "" and "line 2" in r.stderr


def test_unknown_group_rejected_before_any_call(loader):
    r, log = loader(HEADER + "alice,Alice,domain-admins,Welcome2026\n")
    assert r.returncode == 2 and log == ""


def test_bad_display_name_and_password_rejected(loader):
    assert loader(HEADER + "alice,$(id),staff,Welcome2026\n")[0].returncode == 2
    assert loader(HEADER + "alice,Alice,staff,\n")[0].returncode == 2
    assert loader(HEADER + "alice,Alice,staff,ab\n")[0].returncode == 2  # too short


def test_a_bad_line_after_good_ones_still_stops_everything(loader):
    r, log = loader(HEADER + "alice,Alice,staff,Welcome2026\nbad user,Bob,staff,Welcome2026\n")
    assert r.returncode == 2 and log == ""


def test_missing_header_rejected(loader):
    assert loader("alice,Alice,staff,Welcome2026\n")[0].returncode == 2


def test_shipped_users_csv_is_valid(loader):
    r, log = loader(path=CSV)
    assert r.returncode == 0, r.stderr
    assert log.count("user create") >= 6


def test_at_least_two_users_use_the_attack_wordlists():
    users = set((REPO / "scaffold/sslab/data/users.txt").read_text().split())
    passwords = set((REPO / "scaffold/sslab/data/passwords.txt").read_text().split())
    rows = [ln.split(",") for ln in CSV.read_text().splitlines()[1:] if ln and not ln.startswith("#")]
    weak = [r[0] for r in rows if r[0] in users and r[3] in passwords]
    assert len(weak) >= 2, weak


def test_csv_uses_only_lab_internal_data():
    text = CSV.read_text()
    assert "@" not in text.replace("@lab.internal", "")


def test_users_get_a_mail_address_in_the_lab_domain(loader):
    r, log = loader(HEADER + "alice,Alice Nguyen,staff,Welcome2026\n")
    assert r.returncode == 0
    assert "--mail-address=alice@lab.internal" in log
