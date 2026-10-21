# 03: Proxmox

## What you will build

`pve01`: Proxmox VE running inside VMware, hosting every Linux service and the Docker VM in this lab.

## Why

Proxmox is where you will later build, snapshot and restore guests, which is a core skill this unit teaches.
Running it nested means the whole estate fits on one shared workstation.

## Steps

1. Create a new VM: 8 vCPU, 16 GB RAM, 250 GB disk, one network adapter on `LAN-LAB`.
2. **Enable nested virtualisation** for this VM specifically (VMware Workstation: VM settings > Processors >
   "Virtualize Intel VT-x/EPT or AMD-V/RVI").
3. Install Proxmox VE from the official ISO, with a static address `10.10.10.5/24`, gateway `10.10.10.1`.
4. Add your SSH public key to `/root/.ssh/authorized_keys` on `pve01` (copy it from `admin01` once built, or
   paste it directly during a console session).
5. Time budget: building Proxmox from ISO to a working console takes about 30 to 45 minutes.

## Check it worked

- `ssh root@10.10.10.5 pveversion` succeeds from `admin01`.
- Inside Proxmox's own shell, `kvm-ok` (or `egrep -c '(vmx|svm)' /proc/cpuinfo`) shows virtualisation is
  available, not emulated.

## If it goes wrong

- Guests inside Proxmox are extremely slow: nested virtualisation is not actually enabled for the VMware
  VM. Recheck VM settings (step 2) and that Memory Integrity is off on the host (guide 01).
- No network: confirm `pve01`'s NIC is attached to `LAN-LAB`, not NAT.
