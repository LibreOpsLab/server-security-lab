# 06: Create the guests

## What you will build

Every LXC container and the Docker VM, created on Proxmox from the inventory, and given the functional
baseline (time, SSH, a metrics exporter).

**Time and difficulty:** 1 to 2 hours, most of it waiting for downloads. Easy to run; this is your first
taste of automation, so the learning is in reading what it does.

## Why

From here on, you describe what you want in the inventory, and the automation does the repetitive parts.
This guide is the first time you see that pattern.

> **What's going on:** `make guests` does not click through Proxmox for you. It copies a small script
> (`lab/proxmox/guest.sh`) to `pve01` and runs it once per guest. The script uses Proxmox's own commands
> (`pct` for containers, `qm` for VMs), so what you learn is exactly what a Proxmox administrator types.
> It checks whether each guest already exists before creating it, so running it again does no harm. That
> property is called **idempotence**, and good automation has it.

## Before you start

- `ssh root@10.10.10.5 pveversion` works from `admin01` (guide 03 and 04 Part B).
- `pve01` can reach the internet through pfSense. It downloads container templates and a cloud image.
  Check: `ssh root@10.10.10.5 ping -c 3 deb.debian.org`.
- Take a snapshot of `pve01` called `before-guests`.

## Steps

1. Read what is about to run. Open `lab/proxmox/guest.sh` and `lab/ansible/playbooks/10-guests.yml`. Write
   down in your evidence three things the script does and one you do not understand.
2. Create the guests:

   ```bash
   cd lab
   make guests
   ```

   This copies `proxmox/guest.sh` to `pve01` and calls it once per guest in
   `inventory/group_vars/all.yml` (`lab_hosts`). Existing guests are left alone, so running it again is safe.

   > **Beginner tip:** This takes a while the first time, because it downloads container templates and a
   > cloud image. Ansible prints `ok` for things already right, `changed` for things it changed, and
   > `failed` for problems, in red. Read the red text. The last lines are a recap by host.

3. Give every guest the functional baseline: correct time, SSH key access, and a monitoring exporter.

   ```bash
   make baseline
   ```

   > **What's going on:** The baseline is the minimum every machine in the lab needs to work: a clock that
   > follows the domain controller, SSH, and an agent that reports metrics. It is deliberately **not
   > hardened**. Password login stays on and no extra locks are added; the security weeks measure that
   > later. Do not tidy it up now.

   > **Beginner tip:** Every guest is told to take its time from `samba-dc01`, which does not exist until
   > guide 07. Until then `chronyc sources` on a guest will show that source as unreachable. That is
   > expected, not an error. Do not "fix" it; guide 08 checks it once the domain controller is up.

   > **Careful:** `admin01` configures itself, so `make baseline` runs some steps with `sudo` on your own
   > machine (see guide 04, Part B, step 8). If `sudo` wants a password, run it as `ANSIBLE_BECOME_ASK_PASS=true make baseline` and type your password
   > when asked.

## Check it worked

- `ssh root@10.10.10.5 pct list` and `qm list` show all eight guests (seven containers, one VM).
- Each guest answers a ping from `admin01` at its address in the inventory:
  `ping -c 1 10.10.10.21` and so on.
- `make baseline` ended with no failed hosts in the recap.

> **Stop and check:** Do not start guide 07 until all eight guests answer a ping. The next guide builds the
> domain controller and assumes the machines are there.

## Evidence to capture

Save in `portfolio/evidence/06-create-the-guests/`:

| File                | What it shows                                                                |
| ------------------- | ---------------------------------------------------------------------------- |
| `reading-notes.md`  | Your three "I understand this" points and one "I do not" about `guest.sh`    |
| `make-guests.txt`   | Output of `make guests 2>&1 \| tee` (see the [welcome guide](00-welcome.md)) |
| `make-baseline.txt` | Output of `make baseline` ending with the recap                              |
| `pct-qm-list.txt`   | Output of `pct list` and `qm list` run on `pve01`                            |
| `pings.txt`         | A ping to each guest from `admin01`                                          |
| `proxmox-tree.png`  | The Proxmox web page with all eight guests running                           |
| `evidence.md`       | Your filled-in evidence log                                                  |

## Explain it in your own words

1. What does "idempotent" mean? Show where `guest.sh` or Ansible does it.
2. Why does the lab put its services in containers rather than giving each its own full VM?
3. Why does the baseline deliberately _not_ harden anything?

## If it goes wrong

- A guest fails to create because the template is missing: run
  `ssh root@10.10.10.5 'pveam update && pveam download local <template-name>'` with the Debian 12 template
  name shown in the error, then re-run `make guests`.
- The Docker VM's cloud image download fails: check `pve01` has internet through pfSense's NAT.
- `make baseline` says `UNREACHABLE` for a host: the guest is not running or the SSH key did not install.
  Start it in Proxmox, or check `ssh -i ~/.ssh/lab_admin root@<its address>` by hand.
- A Proxmox storage name error: the guides assume storage called `local` and `local-lvm`; if your Proxmox
  has different names, tell your lecturer.
