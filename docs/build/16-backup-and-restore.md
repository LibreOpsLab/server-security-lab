# 16: Backup and restore

## What you will build

`pbs01`: Proxmox Backup Server 4 on a **Debian 13 VM in VMware, outside Proxmox**; a nightly job covering the
Proxmox guests; a separate backup of the domain controller; and a proven restore.

**Time and difficulty:** 3 to 4 hours, including building the VM by hand. Medium.

## Why

A backup nobody has restored is a guess, not a backup. This guide makes you prove one works before you need
it to.

> **What's going on:** A **backup** is a copy of your data stored elsewhere; a **restore** is bringing it
> back. Two numbers matter to a business. **RPO** (recovery point objective) is how much work you can afford
> to lose: with a nightly backup, up to a day. **RTO** (recovery time objective) is how long you can afford to
> be down: the restore test measures it for you in seconds. A backup that has never been restored might be
> corrupt, incomplete or unreadable, and you would only find out in a crisis.

> **Why is the backup server outside Proxmox?** A backup stored on the machine it protects is lost with that
> machine. Keeping `pbs01` as its own VM (and in real life, in another building) means a failed hypervisor does
> not take the backups with it. The domain controller is outside Proxmox too, so Proxmox's job cannot see it:
> you back it up separately with Samba's own tool, and learn that different systems need different backups.

## Before you start

- Guides 06, 07 and 10 are complete (all guests exist, and `make verify` was clean for them).
- You have the **Debian 13 netinst ISO** from your lecturer.
- Take a snapshot of `pve01` called `before-make-backup`.
- Check disk space on the workstation: the backup server's disk is 80 GB. Delete old VMware snapshots you no
  longer need.

## Steps

1. **Build the VM by hand.** Follow [Reference: build a minimal Debian 13 VM](debian-vm.md) for `pbs01`
   (`10.10.10.27`, 2 GB RAM, 2 CPUs, 80 GB disk), including the preparation script over SSH. Stop when
   `ssh root@10.10.10.27 hostname` prints `pbs01`. Take a VMware snapshot called `pbs-os-installed`.
2. **Bring it into the lab** (baseline, certificate trust, log shipping) and check it is ready:

   ```bash
   cd lab
   make baseline LIMIT=pbs01
   make trust LIMIT=pbs01
   make monitoring LIMIT=pbs01
   make preflight STAGE=backup
   ```

3. Build the backup server and nightly job:

   ```bash
   make backup
   ```

   > **What's going on:** Ansible installs Proxmox Backup Server from Proxmox's own package repository on
   > Debian 13, creates a datastore (a folder PBS manages) and a backup user, then tells Proxmox VE to use it
   > as storage and to run the nightly job. The Proxmox web page for PBS is at `https://10.10.10.27:8007`.

4. **Back up the domain controller.** Proxmox cannot see it, so use the script (read it first):

   ```bash
   less backup-dc.sh
   make backup-dc
   ```

   It asks Samba for a safe snapshot of the directory, copies it to `~/lab-backups/` on `admin01` and prints a
   checksum. That archive holds every account's password hash: keep it out of the repository.

5. Prove the restore. Pick any guest and restore it to a throwaway copy (replace `122` with a real VMID from
   your inventory):

   ```bash
   ssh root@10.10.10.5
   /root/lab/restore-test.sh 122 --rto 600   # 122 is auth01
   ```

   > **What's going on:** The script restores the latest backup into a scratch guest with its network
   > _unplugged_ (so it cannot clash with the real one), times it against your recovery goal (`--rto 600`
   > is 600 seconds), then deletes the scratch guest.

   > **Beginner tip:** Choose a small guest the first time (`auth01` is `122`). Restoring `docker01` is
   > slower and heavier.

## Check it worked

The restore test prints `PASS` with the number of seconds it took, and cleans up after itself (no leftover
scratch guest). Check with `qm list` and `pct list` on `pve01`.
`make backup-dc` prints a checksum and the archive's file list, and `make verify` includes the backup server.

## Evidence to capture

> **Beginner tip:** `make evidence GUIDE=16` (from `lab/`) runs the read-only commands for you and saves them, stamped with your name, the date and the machine, in `auto-evidence.txt` in your evidence folder. Read it before you commit. It does not replace your screenshots, your notes or your own explanation.

Save in `portfolio/evidence/16-backup-and-restore/`:

| File                 | What it shows                                                                    |
| -------------------- | -------------------------------------------------------------------------------- |
| `debian-install.png` | The finished Debian 13 install for `pbs01`: `cat /etc/os-release` on its console |
| `prep-script.txt`    | The `ssh ... bash -s` run from the [Debian VM reference](debian-vm.md)           |
| `preflight.txt`      | The `make preflight STAGE=backup` run, all `PASS`                                |
| `make-backup.txt`    | Output of `make backup` ending with the recap                                    |
| `backup-job.png`     | The nightly job in Proxmox (**Datacenter > Backup**)                             |
| `backup-dc.txt`      | The `make backup-dc` output: checksum and file list (never the archive itself)   |
| `pbs-web.png`        | The PBS web page at port 8007 with the `lab` datastore                           |
| `restore-test.txt`   | The full `restore-test.sh` output ending in `PASS` and the time taken            |
| `after-cleanup.txt`  | `pct list` / `qm list` showing no scratch guest remains                          |
| `evidence.md`        | Your filled-in evidence log, including the restore time in seconds               |

## Explain it in your own words

1. In your own words, what is RPO and what is RTO? What are the lab's values?
2. Why restore with the network unplugged?
3. Why does the domain controller need a different backup from the Proxmox guests?
4. If the building were destroyed, what is the one thing still missing from this backup plan? (Hint: where
   does the backup live?)

## If it goes wrong

**Run this first:** `make preflight STAGE=backup`. Once it works, run `make evidence GUIDE=16`.

- The PBS web page at `https://10.10.10.27:8007` does not load: `ssh root@10.10.10.27 systemctl status proxmox-backup-proxy`.
  If `make backup` failed earlier, read its last error: a repository or key problem usually means `pbs01`
  cannot reach `enterprise.proxmox.com` or `download.proxmox.com` (check internet from the VM).
- `make backup` fails on the repository: confirm the VM is Debian 13 (`cat /etc/os-release`). The lab uses the
  `trixie` repository; a Debian 12 machine will not work.
- Proxmox VE cannot add the backup storage: it needs the PBS fingerprint. Re-run `make backup`, which fetches it,
  and check the time on `pve01` and `pbs01` is in sync (`chronyc tracking` on both).
- `restore-test.sh` says it refuses to run: it protects against clobbering a real guest. Read its message;
  pick a different scratch VMID if told to.
- The first backup runs overnight: use **Datacenter > Backup > Run now** in Proxmox to make one straight
  away, then run the restore test.
- `make backup-dc` fails: check `samba-ad-dc` is running on the DC
  (`ssh root@10.10.10.21 systemctl status samba-ad-dc`).
- Fallback if PBS will not work at all: use local storage with `backup-jobs.sh --local` (see
  `lab/proxmox/README.md`). Note in your evidence that you used the fallback and why.

### Where to look

| What                         | Command                                                                       |
| ---------------------------- | ----------------------------------------------------------------------------- |
| PBS services (on `pbs01`)    | `systemctl status proxmox-backup proxmox-backup-proxy`                        |
| PBS log                      | `journalctl -u proxmox-backup-proxy -n 50 --no-pager`                         |
| Datastore                    | `proxmox-backup-manager datastore list`                                       |
| Backup storage (on `pve01`)  | `pvesm status`                                                                |
| Backup task log (on `pve01`) | **Datacenter > Node > Task History** in the web page, or `ls /var/log/vzdump` |
