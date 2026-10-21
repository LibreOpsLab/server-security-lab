# Proxmox guest creation

`guest.sh` creates one LXC container or cloud-init VM on the Proxmox host and is safe to run again: an
existing guest is left alone. You do not normally run it by hand. `make guests` (from `lab/`) copies it to
`pve01` and calls it once per guest with the values in `inventory/group_vars/all.yml`.

Why a shell script and not the Proxmox API? It uses the same `pct` and `qm` commands you will meet in the
Proxmox documentation, needs no API token, and can be tested here with fake commands.

See `docs/build/06-create-the-guests.md` for what this does and how to check it.
