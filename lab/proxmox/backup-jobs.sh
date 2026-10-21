#!/usr/bin/env bash
# Set up nightly backups of the lab guests on the Proxmox host. Safe to re-run.
#
# Usage: backup-jobs.sh --vmids 121,122,... --server PBS_IP --fingerprint FP      (back up to Proxmox Backup Server)
#        backup-jobs.sh --vmids 121,122,... --local                               (fallback: back up to local storage)
# Environment: PBS_PASSWORD (required unless --local) is written to Proxmox's private password file for the
# storage; it is never put on a command line. PW_DIR overrides /etc/pve/priv/storage (for tests).
set -euo pipefail

vmids="" server="" fingerprint="" local_only=0 schedule="02:00"
while [ $# -gt 0 ]; do
  case $1 in
    --vmids) vmids=${2:?--vmids needs a list}; shift 2 ;;
    --server) server=${2:?--server needs an address}; shift 2 ;;
    --fingerprint) fingerprint=${2:?--fingerprint needs a value}; shift 2 ;;
    --local) local_only=1; shift ;;
    --schedule) schedule=${2:?}; shift 2 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
[[ $vmids =~ ^[0-9]+(,[0-9]+)*$ ]] || { echo "--vmids must be a comma-separated list of numbers" >&2; exit 2; }

storage=local
if [ "$local_only" = 0 ]; then
  storage=lab-pbs
  [ -n "$server" ] && [ -n "$fingerprint" ] || { echo "--server and --fingerprint are required (or use --local)" >&2; exit 2; }
  [ -n "${PBS_PASSWORD:-}" ] || { echo "set PBS_PASSWORD in the environment" >&2; exit 2; }
  if ! pvesm status | grep -q "^$storage "; then
    pw_dir=${PW_DIR:-/etc/pve/priv/storage}
    mkdir -p "$pw_dir"
    (umask 077; printf '%s' "$PBS_PASSWORD" >"$pw_dir/$storage.pw")
    pvesm add pbs "$storage" --server "$server" --datastore lab --username backup@pbs --fingerprint "$fingerprint"
    echo "added storage $storage"
  fi
fi

if pvesh get /cluster/backup --output-format json | grep -q lab-nightly; then
  echo "kept backup job lab-nightly"
else
  pvesh create /cluster/backup --id lab-nightly --vmid "$vmids" --storage "$storage" \
    --schedule "$schedule" --mode snapshot --compress zstd --enabled 1
  echo "created backup job lab-nightly"
fi
