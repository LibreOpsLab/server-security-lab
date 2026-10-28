#!/usr/bin/env bash
# Check that a build stage is ready to run, BEFORE you run it, and say what to fix if not.
# Usage: preflight.sh STAGE [HOST]   where STAGE is one of: guests baseline debian-vm identity services apps monitoring backup
# (debian-vm needs a HOST: samba-dc01 or pbs01; it checks a hand-built Debian VM before Ansible touches it)
#
# Each line is PASS or FAIL, like `make verify`. Any FAIL makes this exit 1. It changes nothing.
# Run it from the lab/ folder on admin01:  make preflight STAGE=identity
set -uo pipefail
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root=$(cd "$here/.." && pwd)
gv=$root/lab/inventory/group_vars/all.yml
lab_ip() { sed -nE "s/^  $1: \{.*ip: ([0-9.]+).*/\1/p" "$gv" | head -1; }
domain=$(sed -nE 's/^lab_domain: *(.*)$/\1/p' "$gv" | head -1)

stage=${1:-}
hostarg=${2:-}
failed=0
ok() { printf 'PASS %s\n' "$*"; }
bad() { printf 'FAIL %s\n' "$*"; failed=$((failed + 1)); }

have_tool() { if command -v "$1" >/dev/null 2>&1; then ok "tool $1 is installed"; else bad "tool $1 is missing: sudo apt install -y ${2:-$1}"; fi; }
have_secret() { if [ -s "$root/lab/secrets/$1" ]; then ok "secret $1 exists"; else bad "secret $1 is missing: run scripts/gen-secrets.sh (guide 05)"; fi; }
can_ssh() { # host [user]
  local ip
  ip=$(lab_ip "$1")
  [ -n "$ip" ] || { bad "$1 is not in the inventory"; return; }
  if ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new "${2:-root}@$ip" true 2>/dev/null; then
    ok "ssh to $1 ($ip) works with the lab key"
  else
    bad "ssh to $1 ($ip) failed: is it running, and is the key installed? (try: ssh ${2:-root}@$ip)"
  fi
}
reaches() { # host
  local ip
  ip=$(lab_ip "$1")
  if ping -c 1 -W 2 "$ip" >/dev/null 2>&1; then ok "$1 ($ip) answers a ping"; else bad "$1 ($ip) does not answer a ping: is the guest running?"; fi
}
remote_has_internet() { # host [user]
  local ip
  ip=$(lab_ip "$1")
  if ssh -o BatchMode=yes -o ConnectTimeout=5 "${2:-root}@$ip" 'curl -fsS -m 10 -o /dev/null https://deb.debian.org/ || curl -fsS -m 10 -o /dev/null http://archive.ubuntu.com/' 2>/dev/null; then
    ok "$1 can reach the internet (package mirrors)"
  else
    bad "$1 cannot reach the package mirrors: check pfSense is running, and $1's gateway and DNS"
  fi
}
remote_time_ok() { # host
  local ip then off
  ip=$(lab_ip "$1")
  then=$(ssh -o BatchMode=yes -o ConnectTimeout=5 root@"$ip" date +%s 2>/dev/null) || { bad "could not read the clock on $1"; return; }
  off=$((then - $(date +%s)))
  off=${off#-}
  if [ "$off" -le 120 ]; then ok "$1's clock is within 2 minutes of admin01 (${off}s)"; else bad "$1's clock is ${off}s away from admin01: fix time first (guide 08)"; fi
}
disk_free_gb() { # host min [user]
  local ip free
  ip=$(lab_ip "$1")
  free=$(ssh -o BatchMode=yes -o ConnectTimeout=5 "${3:-root}@$ip" "df -BG --output=avail / | tail -1 | tr -dc 0-9" 2>/dev/null) || { bad "could not read disk space on $1"; return; }
  if [ "${free:-0}" -ge "$2" ]; then ok "$1 has ${free} GB free (needs $2)"; else bad "$1 has only ${free:-0} GB free (needs $2)"; fi
}

common() {
  have_tool ansible-playbook ansible
  have_tool ssh openssh-client
  if [ -f "$HOME/.ssh/lab_admin" ]; then ok "SSH key ~/.ssh/lab_admin exists"; else bad "SSH key ~/.ssh/lab_admin is missing: guide 04, Part B"; fi
  have_secret samba_admin_password
}

case $stage in
  guests)
    common
    can_ssh pve01
    remote_has_internet pve01
    disk_free_gb pve01 40 ;;
  baseline)
    common
    for h in auth01 radius01 mon01 mail01 files01; do reaches "$h"; can_ssh "$h"; done
    reaches docker01
    can_ssh docker01 ubuntu ;;
  debian-vm)
    case $hostarg in samba-dc01 | pbs01) ;; *) echo "usage: preflight.sh debian-vm samba-dc01|pbs01" >&2; exit 2 ;; esac
    common
    reaches "$hostarg"
    can_ssh "$hostarg"
    remote_has_internet "$hostarg"
    disk_free_gb "$hostarg" 5
    remote_time_ok "$hostarg" ;;
  identity)
    common
    reaches samba-dc01
    can_ssh samba-dc01
    remote_has_internet samba-dc01
    remote_time_ok samba-dc01
    disk_free_gb samba-dc01 5
    if [ -s "$root/lab/secrets/ca/intermediate/certs/intermediate.cert.pem" ]; then ok "the lab CA exists"; else bad "the lab CA is missing: scripts/gen-secrets.sh (guide 05)"; fi ;;
  services)
    common
    if getent hosts "samba-dc01.$domain" >/dev/null; then ok "samba-dc01.$domain resolves"; else bad "samba-dc01.$domain does not resolve: build identity first and check admin01's DNS (guides 07 and 08)"; fi
    for h in auth01 mail01 files01 radius01; do reaches "$h"; can_ssh "$h"; remote_time_ok "$h"; done
    if ldapsearch -x -H "ldaps://samba-dc01.$domain" -s base -b "" namingContexts 2>/dev/null | grep -q namingContexts; then ok "LDAPS to the domain controller works"; else bad "LDAPS to the domain controller failed: run make identity and make trust first"; fi ;;
  apps)
    common
    reaches docker01
    can_ssh docker01 ubuntu
    remote_has_internet docker01 ubuntu
    disk_free_gb docker01 15 ubuntu
    if curl -fsS -m 10 -o /dev/null "https://auth.$domain/" 2>/dev/null; then ok "the sign-in portal answers"; else bad "https://auth.$domain/ does not answer: build single sign-on first (make sso, guide 11)"; fi ;;
  monitoring)
    common
    reaches mon01
    can_ssh mon01
    remote_has_internet mon01
    if curl -fsS -m 10 -o /dev/null -k "https://grafana.$domain/" 2>/dev/null; then ok "Traefik serves grafana.$domain"; else bad "https://grafana.$domain/ does not answer: build the apps first (make apps, guide 10)"; fi ;;
  backup)
    common
    reaches pbs01
    can_ssh pbs01
    remote_has_internet pbs01
    disk_free_gb pbs01 20
    can_ssh pve01 ;;
  *)
    echo "usage: preflight.sh guests|baseline|debian-vm HOST|identity|services|apps|monitoring|backup" >&2
    exit 2 ;;
esac

echo
if [ "$failed" -eq 0 ]; then
  echo "Ready: $stage"
else
  echo "Not ready: $failed problem(s) above. Fix them, then run this again."
  exit 1
fi
