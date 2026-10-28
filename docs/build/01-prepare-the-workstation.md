# 01: Prepare the workstation

## What you will build

Nothing yet, visibly, but this is where everything else becomes possible: nested virtualisation turned on,
and the network pieces VMware needs.

## Why

Proxmox runs as a VM inside VMware. For its own guests to run at a reasonable speed, VMware's virtual CPU
has to pass through hardware virtualisation instead of emulating it. Windows also ships security features
that specifically block nested virtualisation.

## Steps

1. Allow exection of PowerShell scripts:

  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
  ```

2. Disable Virtualisation Security to allow Nest Virtulisation to function. Run this script in PowerShell:

   ```terminal
   .\scripts\Set-NestedVirtualisation.ps1
   ```

3. Confirm hardware virtualisation is on in the firmware (Task Manager > Performance > CPU >
   "Virtualization: Enabled").
4. Turn off **Memory Integrity** (Windows Security > Device security > Core isolation). It conflicts with
   nested virtualisation. Reboot.
5. In VMware Workstation, create a **LAN Segment** named `LAN-LAB`. This is the private network every lab
   guest attaches to.
6. Note which of your workstation's two NICs is for the internet and which is for the lab; you will choose
   the internet one for VMware's NAT network in the next guide.

## Check it worked

- `systeminfo | findstr /i "Hyper-V"` or Task Manager shows virtualization enabled.
- The LAN Segment `LAN-LAB` exists in VMware's Virtual Network Editor.

## If it goes wrong

- A VM you create later for Proxmox refuses to start a nested guest, or is extremely slow: Memory Integrity
  is usually still on, or virtualisation is off in firmware. Recheck both and reboot.
- No LAN Segment option: your VMware Workstation edition or version may need the Virtual Network Editor run
  as administrator once first.
