import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parents[2]
GUEST = REPO / "lab" / "proxmox" / "guest.sh"

FAKE = """#!/usr/bin/env bash
# Fake Proxmox command: logs arguments, remembers created guests in $STATE.
name=$(basename "$0")
echo "$name $*" >>"$LOG"
case "$name $1" in
  "pveam list") echo "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst  120MB" ;;
  "pct status"|"qm status") [ -e "$STATE/$name-$2" ] || exit 2 ;;
  "pct create"|"qm create") touch "$STATE/$name-$2" ;;
esac
exit 0
"""


@pytest.fixture
def pve(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for n in ("pct", "qm", "pveam"):
        (bin_dir / n).write_text(FAKE)
        (bin_dir / n).chmod(0o755)
    (tmp_path / "state").mkdir()
    image = tmp_path / "noble.img"
    image.write_text("img")
    key = tmp_path / "lab_admin.pub"
    key.write_text("ssh-ed25519 AAAA test")
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "LOG": str(tmp_path / "log"),
           "STATE": str(tmp_path / "state"), "CLOUD_IMAGE": str(image), "SSH_KEY": str(key)}

    def run(*args):
        return subprocess.run([str(GUEST), *args], env=env, capture_output=True, text=True)

    def log():
        p = tmp_path / "log"
        return p.read_text() if p.exists() else ""

    return run, log


def test_lxc_created_with_static_ip_dns_and_features(pve):
    run, log = pve
    r = run("lxc", "122", "auth01", "10.10.10.22", "512", "1", "4")
    assert r.returncode == 0, r.stderr
    line = next(ln for ln in log().splitlines() if ln.startswith("pct create"))
    for part in ("pct create 122", "debian-12-standard", "--hostname auth01", "--memory 512", "--cores 1",
                 "ip=10.10.10.22/24,gw=10.10.10.1", "--nameserver 10.10.10.21 10.10.10.1", "--features nesting=1",
                 "--unprivileged 1", "--onboot 1"):
        assert part in line, part


def test_privileged_flag_turns_off_unprivileged(pve):
    run, log = pve
    assert run("lxc", "121", "samba-dc01", "10.10.10.21", "1024", "1", "8", "--privileged").returncode == 0
    assert "--unprivileged 0" in log()


def test_existing_guest_is_kept_not_recreated(pve):
    run, log = pve
    run("lxc", "122", "auth01", "10.10.10.22", "512", "1", "4")
    before = log().count("pct create")
    again = run("lxc", "122", "auth01", "10.10.10.22", "512", "1", "4")
    assert again.returncode == 0 and "kept auth01" in again.stdout
    assert log().count("pct create") == before == 1


def test_vm_uses_cloud_image_and_cloud_init_ip(pve):
    run, log = pve
    r = run("vm", "130", "docker01", "10.10.10.30", "5120", "2", "40")
    assert r.returncode == 0, r.stderr
    text = log()
    assert "qm create 130" in text and "--name docker01" in text and "--memory 5120" in text
    assert "qm importdisk 130" in text
    assert "ip=10.10.10.30/24,gw=10.10.10.1" in text and "--sshkeys" in text
    assert "qm resize 130 scsi0 40G" in text and "qm start 130" in text


def test_unknown_kind_exits_2_with_usage(pve):
    run, _ = pve
    r = run("container", "1", "x", "10.10.10.9", "1", "1", "1")
    assert r.returncode == 2 and "usage" in r.stderr.lower()


@pytest.mark.parametrize("args", [
    ("lxc", "abc", "x", "10.10.10.9", "512", "1", "4"),
    ("lxc", "122", "bad name; id", "10.10.10.9", "512", "1", "4"),
    ("lxc", "122", "x", "10.10.10.999", "512", "1", "4"),
    ("lxc", "122", "x", "10.10.10.9", "lots", "1", "4"),
])
def test_bad_arguments_rejected_before_any_proxmox_call(pve, args):
    run, log = pve
    r = run(*args)
    assert r.returncode == 2 and log() == ""


def test_guest_playbook_calls_the_script_for_every_proxmox_guest():
    text = (REPO / "lab" / "ansible" / "playbooks" / "10-guests.yml").read_text()
    assert "guest.sh" in text and "lab_hosts" in text and "debian-13-standard" in text
    assert "samba_dc_privileged" not in text  # the domain controller is a VMware VM, not a container
