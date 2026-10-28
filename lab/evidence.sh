#!/usr/bin/env bash
# Collect the command-line evidence for one build guide into portfolio/evidence/NN-name/auto-evidence.txt.
# Usage (from the lab/ folder on admin01):   ./evidence.sh 07        or   make evidence GUIDE=07
#
# It runs read-only commands that prove what your lab looks like right now, and stamps them with your name,
# this machine, the date and the repository commit. It NEVER prints a secret.
#
# This SUPPLEMENTS your evidence, it does not replace it. You still need the screenshots the guide asks for,
# your evidence.md (what you did, what went wrong, and your own explanation), and you must read the output
# before you commit it. Output you cannot explain is not evidence of learning.
set -uo pipefail
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root=$(cd "$here/.." && pwd)
gv=$root/lab/inventory/group_vars/all.yml
lab_ip() { sed -nE "s/^  $1: \{.*ip: ([0-9.]+).*/\1/p" "$gv" | head -1; }
domain=$(sed -nE 's/^lab_domain: *(.*)$/\1/p' "$gv" | head -1)

guide=${1:-}
[[ $guide =~ ^[0-9]{2}$ ]] || { echo "usage: evidence.sh NN   (the guide number, for example 07)" >&2; exit 2; }
guide_file=$(find "$root/docs/build" -maxdepth 1 -name "$guide-*.md" | head -1)
[ -n "$guide_file" ] || { echo "no build guide numbered $guide" >&2; exit 2; }
name=$(basename "$guide_file" .md)
dir=$root/portfolio/evidence/$name
mkdir -p "$dir"
out=$dir/auto-evidence.txt

# Run one read-only command and record the command, its output and its exit code.
run() { # label, then the command and its arguments
  local label=$1
  shift
  {
    printf '\n### %s\n$ %s\n' "$label" "$*"
    timeout 60 "$@" 2>&1 | head -n 60
    printf '[exit %s]\n' "${PIPESTATUS[0]}"
  } >>"$out"
}
ssh_run() { # label, host, [user], remote command
  local label=$1 host=$2 user=root
  shift 2
  if [ "$1" = "--user" ]; then user=$2; shift 2; fi
  run "$label" ssh -o BatchMode=yes -o ConnectTimeout=5 "$user@$(lab_ip "$host")" "$*"
}

{
  echo "# Automatic evidence for guide $guide ($name)"
  echo "Student:    $(git -C "$root" config user.name 2>/dev/null || echo unknown)"
  echo "Machine:    $(hostname)   user: $(id -un)"
  echo "Collected:  $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo "Commit:     $(git -C "$root" rev-parse --short HEAD 2>/dev/null || echo unknown)  branch: $(git -C "$root" branch --show-current 2>/dev/null)"
  echo "Note: this file supplements your evidence.md; it does not replace screenshots or your own explanation."
} >"$out"

case $guide in
  04)
    run "Network addresses on admin01" ip -br addr
    run "Ansible version" ansible --version
    run "Public key fingerprint (never the private key)" ssh-keygen -lf "$HOME/.ssh/lab_admin.pub"
    ssh_run "Proxmox answers over SSH without a password" pve01 pveversion ;;
  05)
    run "Which repository is origin" git -C "$root" remote -v
    run "Names of the generated secrets (not their contents)" ls "$root/lab/secrets"
    run "The CA chain verifies" openssl verify -CAfile "$root/lab/secrets/ca/root/certs/ca.cert.pem" "$root/lab/secrets/ca/intermediate/certs/intermediate.cert.pem"
    run "Git ignores the secrets folder" git -C "$root" status --short ;;
  06)
    ssh_run "Containers on Proxmox" pve01 pct list
    ssh_run "Virtual machines on Proxmox" pve01 qm list
    for h in samba-dc01 auth01 radius01 mon01 mail01 files01 pbs01 docker01; do
      run "Ping $h" ping -c 2 -W 2 "$(lab_ip "$h")"
    done ;;
  07)
    run "Directory answers over LDAPS" ldapsearch -x -H "ldaps://samba-dc01.$domain" -s base -b "" namingContexts
    ssh_run "Users in the directory (names only)" samba-dc01 samba-tool user list
    ssh_run "Domain functional level" samba-dc01 samba-tool domain level show ;;
  08)
    run "DNS via pfSense" dig +short "samba-dc01.$domain" @10.10.10.1
    run "DNS via the domain controller" dig +short "samba-dc01.$domain" @"$(lab_ip samba-dc01)"
    ssh_run "Time sources on mail01" mail01 chronyc sources
    ssh_run "Time sources on the domain controller" samba-dc01 chronyc sources ;;
  09)
    run "Allowed site through the proxy" curl -sS -m 15 -x http://10.10.10.1:3128 -I https://example.com
    run "Blocked site through the proxy (expect 403)" curl -sS -m 15 -x http://10.10.10.1:3128 -I http://example-blocked.test ;;
  10)
    ssh_run "Containers on docker01" docker01 --user ubuntu "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'"
    for h in cloud pdf vault; do run "HTTPS headers for $h.$domain" curl -sS -m 15 -I "https://$h.$domain/"; done ;;
  11)
    run "Sign-in portal answers" curl -sS -m 15 -I "https://auth.$domain/"
    ssh_run "Authelia service state" auth01 systemctl is-active authelia ;;
  12)
    run "IMAPS handshake (first lines)" bash -c "openssl s_client -connect mail01.$domain:993 </dev/null 2>&1 | head -n 25"
    run "SPF record" dig TXT "$domain" +short
    run "DKIM record" dig TXT "lab._domainkey.$domain" +short
    ssh_run "Mail service state" mail01 "systemctl is-active postfix dovecot opendkim opendmarc" ;;
  13)
    run "Share list (no password)" smbclient -N -L "//files01.$domain"
    ssh_run "File server service state" files01 "systemctl is-active smbd ssh" ;;
  14)
    ssh_run "RADIUS service state" radius01 "systemctl is-active freeradius winbind"
    echo "(The eapol_test SUCCESS/reject output needs a user password, so run it yourself and save it; see guide 14.)" >>"$out" ;;
  15)
    run "Prometheus targets" curl -sS -m 15 "http://$(lab_ip mon01):9090/api/v1/targets?state=active" -o /dev/null -w 'HTTP %{http_code}\n'
    run "Grafana health" curl -sS -m 15 -k "https://grafana.$domain/api/health"
    ssh_run "Monitoring services on mon01" mon01 "systemctl is-active prometheus alertmanager loki grafana-server" ;;
  16)
    ssh_run "Proxmox storage (includes the backup server)" pve01 pvesm status
    ssh_run "Backup jobs" pve01 pvesh get /cluster/backup --output-format json
    ssh_run "PBS service on the backup server" pbs01 "systemctl is-active proxmox-backup proxmox-backup-proxy" ;;
  18)
    run "Full verify run" "$root/lab/verify/verify.sh" ;;
  *)
    echo "(No automatic collection is defined for guide $guide. Follow the Evidence table in the guide by hand.)" >>"$out" ;;
esac

# Never leave a secret behind: warn if the output looks like it holds one.
if grep -qiE 'BEGIN [A-Z ]*PRIVATE KEY|password[=:] *[^ ]+|secret[=:] *[^ ]+' "$out"; then
  echo "WARNING: $out may contain a secret. Open it, remove the line, and do NOT commit it as it is." >&2
fi
echo "Wrote $out"
echo "Read it, then add your screenshots and evidence.md in the same folder before you commit."
