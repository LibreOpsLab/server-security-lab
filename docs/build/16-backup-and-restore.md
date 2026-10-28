# 16: Backup and restore

## What you will build

`pbs01`: Proxmox Backup Server, a nightly job covering every guest, and a proven restore.

**Time and difficulty:** 1.5 to 2.5 hours. Medium. Backup Server in a container is an unusual layout, so be
ready to use the fallback described at the end.

## Why

A backup nobody has restored is a guess, not a backup. This guide makes you prove one works before you need
it to.

> **What's going on:** A **backup** is a copy of your data stored elsewhere; a **restore** is bringing it
> back. Two numbers matter to a business. **RPO** (recovery point objective) is how much work you can afford
> to lose: with a nightly backup, up to a day. **RTO** (recovery time objective) is how long you can afford to
> be down: the restore test measures it for you in seconds. A backup that has never been restored might be
> corrupt, incomplete or unreadable, and you would only find out in a crisis.

## Before you start

- Guides 06 and 10 are complete (all guests exist).
- Take a snapshot of `pve01` called `before-make-backup`.
- Check disk space: `ssh root@10.10.10.5 df -h`. Backups need room. Delete old VMware snapshots you no
  longer need.

## Steps

1. Build the backup server and nightly job:

   ```bash
   cd lab
   make backup
   ```

2. Prove the restore. Pick any guest and restore it to a throwaway copy (replace `122` with a real VMID from
   your inventory):

   ```bash
   ssh root@10.10.10.5
   /root/lab/restore-test.sh 122 --rto 600
   ```

   > **What's going on:** The script restores the latest backup into a scratch guest with its network
   > _unplugged_ (so it cannot clash with the real one), times it against your recovery goal (`--rto 600`
   > is 600 seconds), then deletes the scratch guest.

   > **Beginner tip:** Choose a small guest the first time (`auth01` is `122`). Restoring `docker01` is
   > slower and heavier.

## Check it worked

The restore test prints `PASS` with the number of seconds it took, and cleans up after itself (no leftover
scratch guest). Check with `qm list` and `pct list` on `pve01`.

## Evidence to capture

Save in `portfolio/evidence/16-backup-and-restore/`:

| File                | What it shows                                                         |
| ------------------- | --------------------------------------------------------------------- |
| `make-backup.txt`   | Output of `make backup` ending with the recap                         |
| `backup-job.png`    | The nightly job in Proxmox (**Datacenter > Backup**)                  |
| `restore-test.txt`  | The full `restore-test.sh` output ending in `PASS` and the time taken |
| `after-cleanup.txt` | `pct list` / `qm list` showing no scratch guest remains               |
| `evidence.md`       | Your filled-in evidence log, including the restore time in seconds    |

## Explain it in your own words

1. In your own words, what is RPO and what is RTO? What are the lab's values?
2. Why restore with the network unplugged?
3. If the building were destroyed, what is the one thing still missing from this backup plan? (Hint: where
   does the backup live?)

## If it goes wrong

- Proxmox Backup Server misbehaves in its container (it is not an officially supported layout): use the
  local-storage fallback in `lab/proxmox/README.md` (`backup-jobs.sh --local`) instead. Note in your
  evidence that you used the fallback and why.
- `restore-test.sh` says it refuses to run: it protects against clobbering a real guest. Read its message;
  pick a different scratch VMID if told to.
- The first backup runs overnight: use **Datacenter > Backup > Run now** in Proxmox to make one straight
  away, then run the restore test.
