#!/usr/bin/env bash
# Finish preparing a hand-built Debian 13 VM (samba-dc01, pbs01) so Ansible can manage it.
#
# You install Debian by hand (guide 04). This script does the repetitive part, and you run it from admin01
# over SSH, as your own user, with sudo. Read it first: it is short and it runs as root on the VM.
#
#   ssh YOURUSER@10.10.10.21 "sudo bash -s -- samba-dc01 '$(cat ~/.ssh/lab_admin.pub)'" < lab/bootstrap/prep-guest.sh
#
# Arguments: HOSTNAME (for example samba-dc01) and the PUBLIC key that Ansible will use (the .pub file).
# It is safe to run again: every step checks before it changes anything. It never prints a secret.
set -euo pipefail

usage() { echo "usage: sudo bash prep-guest.sh HOSTNAME 'ssh-ed25519 AAAA... comment'" >&2; exit 2; }
[ "$(id -u)" -eq 0 ] || { echo "run this as root (use sudo)" >&2; exit 2; }
[ $# -eq 2 ] || usage
name=$1 pubkey=$2
[[ $name =~ ^[a-z][a-z0-9-]{0,62}$ ]] || { echo "invalid hostname: $name" >&2; exit 2; }
[[ $pubkey =~ ^ssh-(ed25519|rsa)\ [A-Za-z0-9+/=]+(\ .*)?$ ]] || { echo "that does not look like a PUBLIC ssh key (a .pub file)" >&2; usage; }
domain=${DOMAIN:-lab.internal}

step() { printf '== %s\n' "$*"; }

step "Check the operating system"
# shellcheck disable=SC1091
. /etc/os-release
if [ "${ID:-}" != debian ] || [ "${VERSION_ID:-}" != 13 ]; then
  echo "this lab expects Debian 13 (found ${PRETTY_NAME:-unknown}). Reinstall with the Debian 13 ISO." >&2
  exit 1
fi

step "Check the network"
ip -4 -br addr show scope global | sed 's/^/   /'
if ! getent hosts deb.debian.org >/dev/null 2>&1; then
  echo "cannot resolve deb.debian.org: check this VM's address, gateway (10.10.10.1) and DNS (10.10.10.1) are set" >&2
  exit 1
fi

step "Install the packages Ansible needs"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq openssh-server sudo python3 python3-apt ca-certificates curl open-vm-tools >/dev/null

step "Set the hostname to $name"
current=$(hostnamectl --static 2>/dev/null || hostname)
[ "$current" = "$name" ] || hostnamectl set-hostname "$name"
ip=$(ip -4 -o addr show scope global | awk '{print $4}' | cut -d/ -f1 | head -1)
if ! grep -qE "^\s*$ip\s+$name\." /etc/hosts; then
  sed -i "/^127\.0\.1\.1\s/d" /etc/hosts
  printf '%s %s.%s %s\n' "$ip" "$name" "$domain" "$name" >>/etc/hosts
fi

step "Let Ansible log in as root with its key"
install -d -m 0700 /root/.ssh
touch /root/.ssh/authorized_keys
chmod 0600 /root/.ssh/authorized_keys
grep -qxF "$pubkey" /root/.ssh/authorized_keys || printf '%s\n' "$pubkey" >>/root/.ssh/authorized_keys
# Key login for root only; passwords for root stay off. (The lab keeps password login ON for ordinary users: see baseline.)
install -d /etc/ssh/sshd_config.d
printf 'PermitRootLogin prohibit-password\n' >/etc/ssh/sshd_config.d/05-lab-root-key.conf
sshd -t
systemctl enable --now ssh >/dev/null 2>&1
systemctl reload ssh

step "Done"
echo "   hostname: $(hostname)   address: ${ip:-unknown}"
echo "   Next, from admin01: ssh root@${ip:-ADDRESS} hostname   (it must work without a password)"
