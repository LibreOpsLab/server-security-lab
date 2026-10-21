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
5. Generate an SSH key pair here (`ssh-keygen -t ed25519`) and copy the public key to `pve01`'s
   `authorized_keys` if you have not already.

## Check it worked

- `ansible --version` runs.
- `ssh root@10.10.10.5 pveversion` works without a password prompt.

## If it goes wrong

- No internet on `admin01`: check the NAT adapter is attached and DHCP is enabled on it in VMware.
