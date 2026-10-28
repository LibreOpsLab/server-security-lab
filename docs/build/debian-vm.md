# Reference: build a minimal Debian 13 VM by hand

Two machines in this lab are **native VMware VMs running Debian 13**, not Proxmox guests: the domain
controller `samba-dc01` (guide 07) and the backup server `pbs01` (guide 16). This page is the shared recipe.
You do the install by hand, then a short script finishes the preparation over SSH.

> **What's going on:** In a real company you would not run your identity system and your backups on the very
> hypervisor they protect. If Proxmox fails, you still need to sign in and you still need your backups. So these
> two live outside it, as ordinary servers. You are also learning two real skills: installing a server
> operating system from nothing, and finishing its setup with a script you run over SSH.

**Time and difficulty:** 45 to 60 minutes per machine the first time. Medium.

## What you need

- The **Debian 13 "netinst"** ISO from your lecturer (see
  [How to prepare for the lab](../instructor/prepare-the-lab.md)). Verify its checksum.
- `pfsense01` running (guide 02) and `admin01` ready (guide 04), because the installer downloads packages
  through the firewall.
- The machine's name, address and size from `lab/inventory/group_vars/all.yml` (the table below repeats them,
  but **the inventory is the source of truth**).

| Machine           | Hostname     | Address       | RAM    | CPUs | Disk  |
| ----------------- | ------------ | ------------- | ------ | ---- | ----- |
| Domain controller | `samba-dc01` | `10.10.10.21` | 1.5 GB | 2    | 20 GB |
| Backup server     | `pbs01`      | `10.10.10.27` | 2 GB   | 2    | 80 GB |

## Part 1: create the VM in VMware

1. **File > New Virtual Machine > Custom.** Guest operating system: **Linux, Debian 13.x 64-bit** (if your
   VMware version does not list it yet, choose the newest Debian 64-bit entry).
2. Give it the RAM, CPUs and disk from the table (store the disk as a single file, thin provisioned).
3. **One network adapter**, on the `LAN-LAB` segment. These machines do not need the NAT network: pfSense gives
   them their way to the internet.
4. Attach the Debian ISO to the virtual DVD drive and power on.

> **Beginner tip:** Click inside the VM window to type into it. Release the mouse with `Ctrl + Alt`.

## Part 2: install Debian

Choose **Install** (the text installer). The installer asks many questions; these are the ones that matter.

| Question                     | Answer                                                                                                 | Why                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| Language, location, keyboard | Yours                                                                                                  |                                                                            |
| Hostname                     | The machine's name, such as `samba-dc01`                                                               | Used everywhere                                                            |
| Domain name                  | `lab.internal`                                                                                         | The lab's domain                                                           |
| Root password                | **Leave it blank**                                                                                     | Disables the root account; your user gets `sudo` instead                   |
| Your user                    | Full name and username of your choice, such as `labadmin`, with a password you will remember           | You will log in as this user first                                         |
| Network                      | If the installer found an address by DHCP, go back and choose **configure manually**                   | A server must have a fixed address                                         |
| IP address, netmask          | The address from the table, `255.255.255.0`                                                            |                                                                            |
| Gateway, DNS                 | `10.10.10.1` for both                                                                                  | pfSense routes and forwards DNS (the DC takes over DNS later, in guide 07) |
| Disk partitioning            | Guided, use the entire disk, all files in one partition                                                | Simple is fine for a lab                                                   |
| Package mirror               | A mirror in your country                                                                               |                                                                            |
| Software selection           | Untick the desktop environment and print server. **Tick "SSH server" and "standard system utilities"** | Servers do not need a desktop; you need SSH                                |
| GRUB                         | Install on the primary disk                                                                            |                                                                            |

> **Careful:** The installer erases the disk it uses. In a VM that is the new virtual disk, which is what you
> want. Write down the username and password you chose, but keep them out of Git.

> **What's going on:** "Minimal" means we install almost nothing: no desktop, no extras. Fewer packages mean
> fewer things that can break, fewer things to patch, and less for an attacker to use. You will see this idea
> again in the hardening weeks.

Reboot when asked, and remove the ISO if the VM boots into the installer again (VM settings > CD/DVD).

## Part 3: finish the preparation with a script, over SSH

Do this on **`admin01`**, not in the VM's console. You will install your key with your own user, then run the
repository's preparation script as root through `sudo`.

1. Check the machine answers (use its address from the table):

   ```bash
   ping -c 2 10.10.10.21
   ```

2. Install the lab SSH key for your user (you type the VM user's password once):

   ```bash
   ssh-copy-id -i ~/.ssh/lab_admin.pub labadmin@10.10.10.21
   ```

   Replace `labadmin` with the user you created.

3. **Read the script before you run it.** It runs as root on another machine.

   ```bash
   less lab/bootstrap/prep-guest.sh
   ```

   Find: where it checks the operating system, where it installs packages, and where it adds your key for root.
   Note one thing it does that surprised you.

4. Run it over SSH. The script is sent to the VM and run there with `sudo`; the quoted part passes your public
   key and the machine's name as arguments:

   ```bash
   ssh -i ~/.ssh/lab_admin labadmin@10.10.10.21 "sudo bash -s -- samba-dc01 '$(cat ~/.ssh/lab_admin.pub)'" < lab/bootstrap/prep-guest.sh
   ```

   > **What's going on:** `bash -s` tells bash to read the script from standard input. `< prep-guest.sh` feeds
   > the file in. Everything after `--` becomes the script's arguments. It is a very common way to run a script
   > on a remote machine without copying it there first.

5. Check Ansible's way in works, without a password:

   ```bash
   ssh root@10.10.10.21 hostname
   ```

   It must print `samba-dc01` (or `pbs01`).

6. Check the machine is ready for the next stage:

   ```bash
   cd lab && make preflight STAGE=debian-vm HOST=samba-dc01
   ```

   (The `HOST=` form is for convenience; you can also run `./preflight.sh debian-vm samba-dc01`.)

> **Evidence:** Save the output of the `ssh ... bash -s` run (add `2>&1 | tee prep-samba-dc01.txt`), the
> `ssh root@... hostname` result, and a screenshot of the VM's settings in VMware.

## Troubleshooting

| Symptom                                         | Likely cause                                     | How to check                                                                              | Fix                                                                                                |
| ----------------------------------------------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| The installer cannot download packages          | The VM cannot reach the internet through pfSense | In the installer, open a shell (`Ctrl+Alt+F2`) and `ping 10.10.10.1`, then `ping 1.1.1.1` | Check pfSense is running and the VM is on `LAN-LAB`; recheck gateway and DNS                       |
| `ping` to the new VM fails from `admin01`       | Wrong address, wrong network, or the VM is off   | `ip -br a` inside the VM console                                                          | Correct the address in `/etc/network/interfaces` (or reinstall); check the adapter is on `LAN-LAB` |
| `ssh-copy-id` says `Permission denied`          | Wrong username or password                       | Log in on the VM's console with the same user                                             | Use the exact user you created                                                                     |
| `Connection refused` on port 22                 | SSH server was not installed                     | On the console: `systemctl status ssh`                                                    | `sudo apt install openssh-server` on the console, then run Part 3                                  |
| The script says "expects Debian 13"             | Wrong ISO                                        | `cat /etc/os-release`                                                                     | Reinstall with the Debian 13 ISO                                                                   |
| The script says "cannot resolve deb.debian.org" | DNS not set                                      | `cat /etc/resolv.conf`                                                                    | Set DNS to `10.10.10.1` and run again                                                              |
| `ssh root@...` asks for a password              | The key was not added for root                   | `sudo cat /root/.ssh/authorized_keys` on the VM                                           | Run the script again; it is safe to repeat                                                         |
| `Host key verification failed`                  | You rebuilt the VM and its fingerprint changed   | The error names the line                                                                  | `ssh-keygen -R 10.10.10.21`, then try again                                                        |
