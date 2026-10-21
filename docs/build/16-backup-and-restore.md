# 16: Backup and restore

## What you will build

`pbs01`: Proxmox Backup Server, a nightly job covering every guest, and a proven restore.

## Why

A backup nobody has restored is a guess, not a backup. This guide makes you prove one works before you need
it to.

## Steps

```bash
cd lab
make backup
```

Then, by hand, pick any guest and prove the restore (replace `122` with a real VMID from your inventory):

```bash
ssh root@10.10.10.5
/root/lab/restore-test.sh 122 --rto 600
```

## Check it worked

The restore test prints `PASS` with the number of seconds it took, and cleans up after itself (no leftover
scratch guest).

## If it goes wrong

- Proxmox Backup Server misbehaves in its container (it is not an officially supported layout): use the
  local-storage fallback in `lab/proxmox/README.md` (`backup-jobs.sh --local`) instead.
