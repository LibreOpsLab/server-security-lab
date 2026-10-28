#!/usr/bin/env bash
# Back up the domain controller. It is a VMware VM outside Proxmox, so Proxmox's nightly job cannot see it:
# a directory is backed up with Samba's own tool, not by copying a disk.
#
# Run from admin01 (lab/ folder):  ./backup-dc.sh            or   make backup-dc
# What it does: asks samba-dc01 for an offline backup (a safe snapshot of the directory databases plus the
# configuration, taken while Samba keeps running), copies the archive to ~/lab-backups/ on admin01, and prints
# its checksum and contents so you can see it is a real backup. It never prints a password.
#
# A backup you have not tested is a guess. Restoring is covered in docs/build/16-backup-and-restore.md.
set -euo pipefail
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
gv=$here/inventory/group_vars/all.yml
ip=$(sed -nE 's/^  samba-dc01: \{.*ip: ([0-9.]+).*/\1/p' "$gv" | head -1)
[ -n "$ip" ] || { echo "samba-dc01 is not in the inventory" >&2; exit 2; }
dest=${BACKUP_DIR:-$HOME/lab-backups}
stamp=$(date -u +%Y%m%dT%H%M%SZ)
remote_dir=/var/backups/samba-lab

mkdir -p "$dest"
chmod 700 "$dest"

echo "== Taking an offline backup on samba-dc01 ($ip)"
ssh -o BatchMode=yes -o ConnectTimeout=10 "root@$ip" "install -d -m 0700 $remote_dir && samba-tool domain backup offline --targetdir=$remote_dir >/dev/null && ls -1t $remote_dir/samba-backup-*.tar.bz2 | head -1" >"$dest/.latest" ||
  { echo "the backup failed: is samba-ad-dc running on samba-dc01? (ssh root@$ip systemctl status samba-ad-dc)" >&2; exit 1; }
remote_file=$(tr -d '\r\n' <"$dest/.latest")
rm -f "$dest/.latest"

echo "== Copying it to $dest"
local_file=$dest/samba-dc01-$stamp.tar.bz2
scp -q -o BatchMode=yes "root@$ip:$remote_file" "$local_file"
chmod 600 "$local_file"

echo "== Checking it"
sha256sum "$local_file"
echo "Contents (first 15 entries):"
tar -tjf "$local_file" | head -n 15
echo
echo "Saved $local_file"
echo "This archive holds every account's password hash: treat it as a secret. Keep it out of the repository."
