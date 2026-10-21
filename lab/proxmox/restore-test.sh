#!/usr/bin/env bash
# Prove a backup restores: restore the latest backup of one guest to a scratch guest, boot it with its network
# unplugged (so it cannot clash with the original), time it against the recovery time objective (RTO), then
# delete the scratch guest.
#
# Usage: restore-test.sh VMID [--rto SECONDS] [--storage lab-pbs] [--target-storage local-lvm]
# The scratch guest is VMID + 1000, so keep VMIDs of 1000 and above free for it.
set -euo pipefail

vmid=${1:?usage: restore-test.sh VMID [--rto SECONDS] [--storage lab-pbs] [--target-storage local-lvm]}
shift
rto=900 storage=lab-pbs target=local-lvm
while [ $# -gt 0 ]; do
  case $1 in
    --rto) rto=${2:?}; shift 2 ;;
    --storage) storage=${2:?}; shift 2 ;;
    --target-storage) target=${2:?}; shift 2 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
[[ $vmid =~ ^[0-9]+$ && $rto =~ ^[0-9]+$ ]] || { echo "VMID and --rto must be numbers" >&2; exit 2; }

if pct status "$vmid" >/dev/null 2>&1; then kind=lxc
elif qm status "$vmid" >/dev/null 2>&1; then kind=vm
else echo "no guest with VMID $vmid" >&2; exit 2; fi

scratch=$((vmid + 1000))

# The scratch guest must not already exist: the cleanup trap below destroys it unconditionally, and must
# never be allowed to destroy something this script did not create.
if { [ "$kind" = lxc ] && pct status "$scratch" >/dev/null 2>&1; } || { [ "$kind" = vm ] && qm status "$scratch" >/dev/null 2>&1; }; then
  echo "guest $scratch already exists: refusing to overwrite or destroy it. Free that VMID first." >&2
  exit 2
fi

# Keep only this guest's backups even if the listing is not filtered, then take the newest.
volid=$(pvesm list "$storage" --vmid "$vmid" | awk -v id="/$vmid/" 'NR > 1 && index($1, id) {print $1}' | sort | tail -1)
[ -n "$volid" ] || { echo "no backup of $vmid found on $storage" >&2; exit 2; }

cleanup() {
  if [ "$kind" = lxc ]; then pct stop "$scratch" >/dev/null 2>&1 || true; pct destroy "$scratch" >/dev/null 2>&1 || true
  else qm stop "$scratch" >/dev/null 2>&1 || true; qm destroy "$scratch" >/dev/null 2>&1 || true; fi
}
trap cleanup EXIT

start=$(date +%s)
if [ "$kind" = lxc ]; then
  pct restore "$scratch" "$volid" --storage "$target"
  pct set "$scratch" --net0 name=eth0,bridge=vmbr0,link_down=1
  pct start "$scratch"
  until pct status "$scratch" | grep -q running; do sleep 2; done
else
  qmrestore "$volid" "$scratch" --storage "$target"
  qm set "$scratch" --net0 virtio,bridge=vmbr0,link_down=1
  qm start "$scratch"
  until qm status "$scratch" | grep -q running; do sleep 2; done
fi
elapsed=$(($(date +%s) - start))

if [ "$elapsed" -lt "$rto" ]; then
  echo "PASS restore of $vmid ($volid) took $elapsed seconds (RTO $rto)"
else
  echo "FAIL restore of $vmid ($volid) took $elapsed seconds (RTO $rto)"
  exit 1
fi
