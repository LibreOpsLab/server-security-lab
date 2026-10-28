# 01: Prepare the workstation

## What you will build

Nothing yet, visibly, but this is where everything else becomes possible: nested virtualisation turned on,
and the network pieces VMware needs.

## Why

Proxmox runs as a VM inside VMware. For its own guests to run at a reasonable speed, VMware's virtual CPU
has to pass through hardware virtualisation instead of emulating it. Windows also ships security features
that can use the same processor features and prevent nested virtualisation from working.

## Steps

1. Open **PowerShell as an administrator**. The preparation script needs elevation to change Windows
   features, boot settings and registry values. Run these commands from the repository root.

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
   ```

2. (Optional) Check the current state. This command is read-only:

   ```powershell
   .\scripts\Set-NestedVirtualisation.ps1 -Mode Check
   ```

3. Actually disable the Windows features that interfere with nested virtualisation:

   ```powershell
   .\scripts\Set-NestedVirtualisation.ps1 -Mode Disable
   ```

   Read the warning, then type `YES` when prompted. The script saves the original settings so they can be
   restored later. It disables Hyper-V-related Windows features, Virtualisation-Based Security, Memory
   Integrity and Credential Guard; running it without `-Mode Disable` only checks the current state.

4. Restart Windows when the script finishes. Then, in the same elevated PowerShell window, verify the
   settings:

   ```powershell
   .\scripts\Set-NestedVirtualisation.ps1 -Mode Check
   ```

   Continue only when the result says `READY`. In the report, Virtualization-based security should be `Off`,
   and `Hypervisor running under Windows` should be `False`. If it says `NOT READY`, do not continue to the
   Proxmox setup. If a policy is listed, capture the report and ask your lecturer; policy-controlled settings
   must be changed by the school's administrator.

   If Windows still reports Virtualization-based security as enabled or running, and no policy is listed,
   the machine may have a firmware-backed VBS lock. Have the BitLocker recovery key available, remain at the
   computer during restart, then run:

   ```powershell
   .\scripts\Set-NestedVirtualisation.ps1 -Mode Disable -UnlockFirmware
   ```

   Confirm the additional warning. Restart and accept the firmware change at the pre-Windows prompt. If no
   prompt appears, or the check still reports `NOT READY`, stop and ask your lecturer; do not keep repeating
   the firmware-unlock step.

5. Confirm hardware virtualisation is enabled in the firmware (Task Manager > Performance > CPU >
   "Virtualization: Enabled"). This is separate from the Windows settings changed by the script.
6. In VMware Workstation, create a **LAN Segment** named `LAN-LAB`. This is the private network every lab
   guest attaches to.
7. Note which of your workstation's two NICs is for the internet and which is for the lab; you will choose
   the internet one for VMware's NAT network in the next guide.

To restore the Windows settings saved before preparation, run
`.\scripts\Set-NestedVirtualisation.ps1 -Mode Restore` from an elevated PowerShell window, then restart.
Restore returns the saved Windows settings; it does not reinstate a firmware lock removed by the optional
unlock step.

## Check it worked

- The script's post-restart check reports `READY`.
- Task Manager shows hardware virtualization enabled.
- The LAN Segment `LAN-LAB` exists in VMware's Virtual Network Editor.

## If it goes wrong

- The script reports `NOT READY`: follow the report's yellow lines and ask your lecturer if a policy or
  firmware lock is preventing the change. If it reports VBS as enabled/running with no policy listed, follow
  the optional firmware-unlock step above. Do not rely on only turning off Memory Integrity in Windows
  Security; other Windows hypervisor features may still be active.
- Proxmox later refuses to start a nested guest, or is extremely slow: confirm this guide's script check
  still reports `READY`, hardware virtualisation is enabled in firmware, and nested virtualisation is
  enabled for the Proxmox VM in VMware (guide 03).
- No LAN Segment option: your VMware Workstation edition or version may need the Virtual Network Editor run
  as administrator once first.
