# Proxmox guest creation

`guest.sh` creates one LXC container or cloud-init VM on the Proxmox host and is safe to run again: an
existing guest is left alone. You do not normally run it by hand. `make guests` (from `lab/`) copies it to
`pve01` and calls it once per guest with the values in `inventory/group_vars/all.yml`.

Why a shell script and not the Proxmox API? It uses the same `pct` and `qm` commands you will meet in the
Proxmox documentation, needs no API token, and can be tested here with fake commands.

See `docs/build/06-create-the-guests.md` for what this does and how to check it.

## Backup and restore

- `backup-jobs.sh` adds the Proxmox Backup Server storage and a nightly job for the guest list `make backup`
  gives it. `restore-test.sh VMID` restores the latest backup to a scratch guest with its network unplugged,
  times it against an RTO, and deletes it.
- **Fallback:** Proxmox Backup Server in a container is not an officially supported layout. If `pbs01` will not
  run well, run `backup-jobs.sh --vmids ... --local`: it uses `vzdump` through the same backup job, writing to the
  Proxmox host's `local` storage. You lose deduplication and the separate backup server, but the restore test works.
