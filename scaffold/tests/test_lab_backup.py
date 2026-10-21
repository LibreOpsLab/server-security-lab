import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parents[2]
LAB = REPO / "lab"
JOBS = LAB / "proxmox" / "backup-jobs.sh"
RESTORE = LAB / "proxmox" / "restore-test.sh"

FAKE = """#!/usr/bin/env bash
# Fake Proxmox tool. Logs calls; keeps tiny state in $STATE.
name=$(basename "$0")
echo "$name $*" >>"$LOG"
case "$name $1" in
  "pvesm status") [ -e "$STATE/storage" ] && echo "lab-pbs  pbs  active" ; echo "local  dir  active" ;;
  "pvesm add") touch "$STATE/storage" ;;
  "pvesm list")
    echo "Volid Format Type Size VMID"
    echo "lab-pbs:backup/ct/122/2026-10-20T01:00:00Z  pbs-ct  backup  1 122"
    echo "lab-pbs:backup/ct/122/2026-10-21T01:00:00Z  pbs-ct  backup  1 122"
    echo "lab-pbs:backup/vm/130/2026-10-21T01:00:00Z  pbs-vm  backup  1 130" ;;
  "pvesh get") [ -e "$STATE/job" ] && echo '[{"id":"lab-nightly"}]' || echo '[]' ;;
  "pvesh create") touch "$STATE/job" ;;
  "pct status") [ "$2" = 122 ] || [ "$2" = 1122 ] && { [ -e "$STATE/failstart" ] && echo "status: stopped" || echo "status: running"; exit 0; } || exit 2 ;;
  "pct start") [ -e "$STATE/failstart" ] && exit 1 ;;
  "qm status") [ "$2" = 130 ] || [ "$2" = 1130 ] && { echo "status: running"; exit 0; } || exit 2 ;;
esac
exit 0
"""


@pytest.fixture
def pve(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for n in ("pvesm", "pvesh", "pct", "qm", "qmrestore", "pveam"):
        (bin_dir / n).write_text(FAKE)
        (bin_dir / n).chmod(0o755)
    (tmp_path / "state").mkdir()
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "LOG": str(tmp_path / "log"),
           "STATE": str(tmp_path / "state"), "PBS_PASSWORD": "not-a-real-secret", "PW_DIR": str(tmp_path / "pw")}

    def run(script, *args, extra=None):
        return subprocess.run([str(script), *args], env={**env, **(extra or {})}, capture_output=True, text=True)

    def log():
        p = tmp_path / "log"
        return p.read_text() if p.exists() else ""

    return run, log, tmp_path / "state"


def test_job_script_adds_pbs_storage_and_a_nightly_job_for_the_listed_guests(pve):
    run, log, _ = pve
    r = run(JOBS, "--vmids", "121,122,130", "--server", "10.10.10.27", "--fingerprint", "AA:BB")
    assert r.returncode == 0, r.stderr
    text = log()
    assert "pvesm add pbs lab-pbs" in text and "--server 10.10.10.27" in text and "--datastore lab" in text
    assert "pvesh create /cluster/backup" in text and "--vmid 121,122,130" in text and "--storage lab-pbs" in text
    assert "--schedule" in text and "--mode snapshot" in text


def test_job_script_is_idempotent(pve):
    run, log, _ = pve
    args = ["--vmids", "121,122", "--server", "10.10.10.27", "--fingerprint", "AA:BB"]
    run(JOBS, *args)
    first = log().count("pvesm add") + log().count("pvesh create")
    run(JOBS, *args)
    assert log().count("pvesm add") + log().count("pvesh create") == first == 2


def test_local_fallback_backs_up_to_local_storage_without_pbs(pve):
    run, log, _ = pve
    assert run(JOBS, "--vmids", "121,122", "--local").returncode == 0
    assert "--storage local" in log() and "pvesm add" not in log()


def test_password_goes_to_the_private_file_not_the_command_line(pve):
    run, log, state = pve
    r = run(JOBS, "--vmids", "121", "--server", "10.10.10.27", "--fingerprint", "AA:BB")
    assert "not-a-real-secret" not in r.stdout + r.stderr + log()
    pw = state.parent / "pw" / "lab-pbs.pw"
    assert pw.read_text() == "not-a-real-secret" and oct(pw.stat().st_mode)[-3:] == "600"


def test_restore_test_restores_latest_backup_of_a_container_unplugged_and_cleans_up(pve):
    run, log, _ = pve
    r = run(RESTORE, "122", "--rto", "600")
    assert r.returncode == 0, r.stderr
    text = log()
    assert "pct restore 1122 lab-pbs:backup/ct/122/2026-10-21T01:00:00Z" in text  # the latest one
    assert "link_down=1" in text
    assert "pct start 1122" in text and "pct destroy 1122" in text
    assert "PASS" in r.stdout and "seconds" in r.stdout


def test_restore_test_handles_a_vm(pve):
    run, log, _ = pve
    r = run(RESTORE, "130", "--rto", "600")
    assert r.returncode == 0, r.stderr
    assert "qmrestore lab-pbs:backup/vm/130/2026-10-21T01:00:00Z 1130" in log() and "qm destroy 1130" in log()


def test_scratch_guest_is_destroyed_even_when_the_start_fails(pve):
    run, log, state = pve
    (state / "failstart").touch()
    r = run(RESTORE, "122", "--rto", "600")
    assert r.returncode != 0 and "pct destroy 1122" in log()


def test_exceeding_the_rto_fails_the_test(pve):
    run, _, _ = pve
    r = run(RESTORE, "122", "--rto", "0")
    assert r.returncode == 1 and "FAIL" in r.stdout


def test_unknown_guest_is_rejected(pve):
    run, _, _ = pve
    assert run(RESTORE, "999").returncode == 2


def test_fallback_is_documented_next_to_the_scripts():
    readme = (LAB / "proxmox" / "README.md").read_text()
    assert "vzdump" in readme and "--local" in readme


def test_pbs_role_installs_from_the_signed_proxmox_repo_and_creates_the_datastore_and_user():
    tasks = (LAB / "ansible/roles/pbs/tasks/main.yml").read_text()
    assert "signed-by" in tasks and "pbs-no-subscription" in tasks and "proxmox-backup-server" in tasks
    assert "datastore create lab" in tasks and "backup@pbs" in tasks and "pbs_admin_password" in tasks
    assert "no_log: true" in tasks


def test_backup_playbook_lists_every_guest_except_the_backup_server_itself():
    play = (LAB / "ansible/playbooks/70-backup.yml").read_text()
    assert "backup-jobs.sh" in play and "restore-test.sh" in play and "pbs_admin_password" in play
    assert "pbs01" in play and "rejectattr" in play  # the backup server is not in its own job
