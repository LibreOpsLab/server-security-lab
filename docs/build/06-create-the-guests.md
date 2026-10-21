# 06: Create the guests

## What you will build

Every LXC container and the Docker VM, created on Proxmox from the inventory.

## Why

From here on, you describe what you want in the inventory, and the automation does the repetitive parts.
This guide is the first time you see that pattern.

## Steps

```bash
cd lab
make guests
```

This copies `proxmox/guest.sh` to `pve01` and calls it once per guest in `inventory/group_vars/all.yml`
(`lab_hosts`). Existing guests are left alone, so running it again is safe.

## Check it worked

- `ssh root@10.10.10.5 pct list` and `qm list` show all eight guests.
- Each guest answers a ping from `admin01` at its address in the inventory.

## If it goes wrong

- A guest fails to create because the template is missing: run `ssh root@10.10.10.5 'pveam update && pveam download local <template-name>'`
  with the Debian 12 template name shown in the error, then re-run `make guests`.
- The Docker VM's cloud image download fails: check `pve01` has internet through pfSense's NAT.
