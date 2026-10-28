# 03: Proxmox

## What you will build

`pve01`: Proxmox VE running inside VMware, hosting every Linux service and the Docker VM in this lab.

**Time and difficulty:** 2 to 3 hours, plus waiting for the installer. Medium. The install itself is easy;
the risk is nested virtualisation not being switched on, which shows up later as "everything is painfully
slow".

> **Do this first:** guide 01 must report `READY`, and `pfsense01` (guide 02) and `admin01` (guide 04,
> Part A) must be running, so that the lab network exists and you can open Proxmox's web page from
> `admin01`.

## Why

Proxmox is where you will later build, snapshot and restore guests, which is a core skill this unit teaches.
Running it nested means the whole estate fits on one shared workstation.

> **What's going on:** Proxmox is a hypervisor, like VMware, but built for servers. It runs two kinds of
> guest. A **VM** is a whole pretend computer. An **LXC container** shares Proxmox's own Linux kernel, so
> it is far lighter: a container can run on 512 MB of RAM. Most of this lab's services are containers for
> that reason. Because Proxmox is itself running in a VMware VM, this is "VMs inside a VM".

## Steps

1. Create a new VM in VMware: 8 vCPU, 12 GB RAM, 160 GB disk, **one** network adapter on `LAN-LAB`.
   Attach the **Proxmox VE 9** ISO (it is built on Debian 13). Do not power it on yet.

   > **Beginner tip:** Choose "Thin provision" or "Allocate disk space as needed" for the 160 GB disk, so it
   > only takes the space it uses. Your 512 GB drive cannot hold several fully-allocated disks.

2. **Enable nested virtualisation** for this VM specifically: VM settings > Processors > tick
   "Virtualize Intel VT-x/EPT or AMD-V/RVI".

   > **Stop and check:** If that box is greyed out or missing, guide 01 did not fully work, or virtualisation
   > is off in the firmware. Go back to guide 01. Do not carry on: Proxmox will install, appear fine, and
   > then run every guest at a crawl.

   > **Evidence:** Screenshot the Processors page with the box ticked.

3. Power on and install Proxmox VE from the ISO, with a static address `10.10.10.5/24`, gateway `10.10.10.1`.
   Use DNS `10.10.10.1` for now. Set a root password you will remember and an email address (any address
   will do for the lab, such as `root@lab.internal`). Choose the hostname `pve01.lab.internal`.

   > **Careful:** The installer erases the disk it uses. In a VM that is the 160 GB virtual disk, which is
   > what you want. Never run a Proxmox install on a real machine you care about.

4. When the installer finishes it reboots and shows the address to use. From `admin01`, open
   `https://10.10.10.5:8006` in a browser (accept the certificate warning) and sign in as `root` with the
   realm **Linux PAM standard authentication**. Dismiss the "no valid subscription" message; the free
   version is fine for the lab.
5. From `admin01`, check you can log in over SSH with the root password:

   ```bash
   ssh root@10.10.10.5 pveversion
   ```

   Part B of [04-admin01.md](04-admin01.md) installs your SSH key on `pve01`. Do that now, then return here.

6. Time budget: building Proxmox from ISO to a working console takes about 30 to 45 minutes.

## Check it worked

- `ssh root@10.10.10.5 pveversion` succeeds from `admin01`.
- Inside Proxmox's own shell, `kvm-ok` (or `egrep -c '(vmx|svm)' /proc/cpuinfo`) shows virtualisation is
  available, not emulated. A result of `1` or higher from the second command means yes; `0` means nested
  virtualisation is not working.
- The web page at `https://10.10.10.5:8006` loads and shows the node `pve01`.

## Evidence to capture

Save in `portfolio/evidence/03-proxmox/`:

| File                       | What it shows                                                        |
| -------------------------- | -------------------------------------------------------------------- |
| `vm-processors.png`        | VMware Processors page with virtualisation ticked                    |
| `pve-web-ui.png`           | Proxmox web page, address bar visible, node `pve01` in the tree      |
| `pveversion.txt`           | `ssh root@10.10.10.5 pveversion` run from `admin01`, with the prompt |
| `virtualisation-check.txt` | The `egrep -c ...` or `kvm-ok` result from inside `pve01`            |
| `evidence.md`              | Your filled-in evidence log                                          |

## Explain it in your own words

1. What is the difference between a VM and an LXC container, and why does the lab use mostly containers?
2. What does "nested virtualisation" mean, and what symptom would tell you it is not working?

## If it goes wrong

- Guests inside Proxmox are extremely slow: nested virtualisation is not actually enabled for the VMware
  VM. Recheck VM settings (step 2) and that Memory Integrity is off on the host (guide 01).
- No network: confirm `pve01`'s NIC is attached to `LAN-LAB`, not NAT, and that `pfsense01` is running.
- The installer cannot find a disk: the 160 GB disk was not attached. Check the VM's hardware list.
- The web page does not load: use `https://` (not `http://`) and port `8006`. Check `ping 10.10.10.5` first.
- Take a snapshot of `pve01` called `working-proxmox` once everything above passes, so a later mistake costs
  minutes, not hours.

### Where to look

| What                         | Command or place                                                             |
| ---------------------------- | ---------------------------------------------------------------------------- |
| Is virtualisation available? | `egrep -c '(vmx\|svm)' /proc/cpuinfo` inside `pve01` (needs to be 1 or more) |
| Proxmox services             | `systemctl status pveproxy pvedaemon`                                        |
| Network address              | `ip -br a` and `cat /etc/network/interfaces`                                 |
| Web page log                 | `journalctl -u pveproxy -n 50 --no-pager`                                    |
