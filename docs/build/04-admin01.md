# 04: admin01

## What you will build

`admin01`: an Ubuntu Desktop VM. This is where you run every `make` command from here on, and later where
the security tools live.

## Why

Keeping the control machine separate from the things it manages is standard practice, and it mirrors how a
real small business would run its administration.

## Steps

1. Create a new VM: 2 vCPU, 3 GB RAM, 40 GB disk, one adapter on `LAN-LAB`, one on VMware NAT (so you can
   fetch packages and this repo).
2. Install Ubuntu Desktop 24.04, static address `10.10.10.10/24` on the lab NIC.
3. Install git and clone this repo (or your own private copy, see
   [05-the-repo-inventory-and-secrets.md](05-the-repo-inventory-and-secrets.md)).
4. Install Ansible: `sudo apt install ansible` (or `pipx install ansible-core`).
5. Confirm `sudo` works without a password prompt for your user (`sudo -n true`), since several playbooks
   use `become: true` locally on this machine (for example the certificate-issuing plays). If it asks for a
   password, either set up passwordless sudo for yourself, or add `--ask-become-pass` (`-K`) to every
   `ansible-playbook` command below.
5. Generate the SSH key pair the automation expects — the name matters, it is read from
   `ansible_ssh_private_key_file` in the inventory:

   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/lab_admin -N ''
   ```

   Copy `~/.ssh/lab_admin.pub` to `pve01`'s `/root/.ssh/lab_admin.pub` (`guest.sh` installs it on every
   guest it creates; `pve01` itself needs it copied by hand once, since nothing created it yet):

   ```bash
   ssh-copy-id -i ~/.ssh/lab_admin.pub root@10.10.10.5
   ```

## Check it worked

- `ansible --version` runs.
- `ssh root@10.10.10.5 pveversion` works without a password prompt.

## If it goes wrong

- No internet on `admin01`: check the NAT adapter is attached and DHCP is enabled on it in VMware.
