#!/usr/bin/env bash
# Create one Proxmox guest, idempotently. Run ON the Proxmox host (pve01); Ansible copies it there and
# calls it with values from the inventory, so the numbers live in one place.
#
# Usage: guest.sh lxc|vm VMID NAME IP RAM_MB CORES DISK_GB [--privileged]
#
# lxc: a Debian 12 container from the Proxmox template store (nesting on; unprivileged unless asked).
# vm : an Ubuntu 24.04 cloud-image VM configured with cloud-init (static IP and your SSH key).
# If the guest already exists the script prints "kept NAME" and changes nothing.
#
# Environment (all optional): STORAGE (local-lvm), BRIDGE (vmbr0), GATEWAY (10.10.10.1), DNS1 (10.10.10.21),
# DNS2 (10.10.10.1), DOMAIN (lab.internal), SSH_KEY (/root/.ssh/lab_admin.pub), CLOUD_IMAGE (path of the
# Ubuntu cloud image; downloaded if missing).
set -euo pipefail

usage() { echo "usage: guest.sh lxc|vm VMID NAME IP RAM_MB CORES DISK_GB [--privileged]" >&2; exit 2; }
[ $# -ge 7 ] || usage
kind=$1 vmid=$2 name=$3 ip=$4 ram=$5 cores=$6 disk=$7 privileged=0
[ "${8:-}" = "--privileged" ] && privileged=1

case $kind in lxc | vm) ;; *) usage ;; esac
[[ $vmid =~ ^[0-9]+$ ]] || { echo "VMID must be a number" >&2; exit 2; }
[[ $name =~ ^[a-z][a-z0-9-]{0,62}$ ]] || { echo "invalid guest name: $name" >&2; exit 2; }
[[ $ip =~ ^(25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1?[0-9]?[0-9])){3}$ ]] || { echo "invalid IP: $ip" >&2; exit 2; }
for v in "$ram" "$cores" "$disk"; do [[ $v =~ ^[0-9]+$ ]] || { echo "RAM, cores and disk must be numbers" >&2; exit 2; }; done

storage=${STORAGE:-local-lvm} bridge=${BRIDGE:-vmbr0} gateway=${GATEWAY:-10.10.10.1}
dns1=${DNS1:-10.10.10.21} dns2=${DNS2:-10.10.10.1} domain=${DOMAIN:-lab.internal}
ssh_key=${SSH_KEY:-/root/.ssh/lab_admin.pub}
image=${CLOUD_IMAGE:-/var/lib/vz/template/iso/noble-server-cloudimg-amd64.img}

if [ "$kind" = lxc ]; then
  if pct status "$vmid" >/dev/null 2>&1; then echo "kept $name"; exit 0; fi
  template=$(pveam list local | awk '/debian-12-standard/ {print $1}' | sort | tail -1)
  [ -n "$template" ] || { echo "no Debian 12 template: run 'pveam update && pveam download local <template>'" >&2; exit 1; }
  unpriv=1
  [ "$privileged" = 1 ] && unpriv=0
  pct create "$vmid" "$template" --hostname "$name" --memory "$ram" --cores "$cores" --rootfs "$storage:$disk" \
    --net0 "name=eth0,bridge=$bridge,ip=$ip/24,gw=$gateway" --nameserver "$dns1 $dns2" --searchdomain "$domain" \
    --features nesting=1 --unprivileged "$unpriv" --ssh-public-keys "$ssh_key" --onboot 1 --start 1
else
  if qm status "$vmid" >/dev/null 2>&1; then echo "kept $name"; exit 0; fi
  if [ ! -f "$image" ]; then
    mkdir -p "$(dirname "$image")"
    wget -q -O "$image" https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img
  fi
  qm create "$vmid" --name "$name" --memory "$ram" --cores "$cores" --net0 "virtio,bridge=$bridge" \
    --scsihw virtio-scsi-pci --agent enabled=1 --ostype l26 --onboot 1
  qm importdisk "$vmid" "$image" "$storage"
  qm set "$vmid" --scsi0 "$storage:vm-$vmid-disk-0" --boot order=scsi0 --ide2 "$storage:cloudinit" \
    --ciuser ubuntu --sshkeys "$ssh_key" --ipconfig0 "ip=$ip/24,gw=$gateway" --nameserver "$dns1 $dns2" --searchdomain "$domain"
  qm resize "$vmid" scsi0 "${disk}G"
  qm start "$vmid"
fi
echo "created $name"
