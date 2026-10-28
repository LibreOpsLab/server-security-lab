# 01: Prepare the workstation

## What you will build

Nothing yet, visibly, but this is where everything else becomes possible: nested virtualisation turned on,
and the private network VMware needs.

**Time and difficulty:** 1 to 2 hours. Easy to follow, but it changes Windows security settings and needs a
restart, so read each warning. If your lab PCs have been prepared already, your lecturer will tell you which
steps to skip; you still do the checks and capture the evidence.

## Why

Proxmox runs as a VM inside VMware. For its own guests to run at a reasonable speed, VMware's virtual CPU
has to pass through hardware virtualisation instead of emulating it. Windows also ships security features
that can use the same processor features and prevent nested virtualisation from working.

> **What's going on:** "Nested virtualisation" is a VM inside a VM. Your PC's CPU has special instructions
> for running VMs fast. Windows' own security features (Virtualization-based Security, Memory Integrity,
> Credential Guard) claim those instructions for themselves, so VMware cannot hand them on to Proxmox. The
> script in this guide turns those Windows features off for the lab.

> **Careful:** You are deliberately switching off protections that normally keep Windows safe. That is
> acceptable here only because this is a dedicated lab PC. Never do this on your personal laptop without
> understanding the trade-off, and the script can put the settings back (see the end of the steps).

## Before you start

- You are on the lab workstation, signed in with an account that can run PowerShell as administrator.
- The repository is cloned (see [DevOps 101](../devops-101.md)).
- You have VMware Workstation installed.
- Take a note of your BitLocker status if the PC uses BitLocker (Settings > Privacy & security > Device
  encryption). The optional firmware step later can ask for the recovery key.

## Steps

1. Open **PowerShell as an administrator** (Start menu, type `PowerShell`, right-click, **Run as
   administrator**). The preparation script needs elevation to change Windows features, boot settings and
   registry values. Move to the repository folder, for example:

   ```powershell
   Set-Location "$HOME\dev\server-security-lab"
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
   ```

   > **What's going on:** By default Windows refuses to run scripts you have not signed. `RemoteSigned`
   > lets scripts you wrote or cloned locally run, and still blocks unsigned scripts downloaded from the
   > internet. `-Scope CurrentUser` limits the change to your account.

2. Check the current state. This command only reads settings; it changes nothing:

   ```powershell
   .\scripts\Set-NestedVirtualisation.ps1 -Mode Check
   ```

   > **Evidence:** Save this "before" report, or take a screenshot. Name it
   > `check-before.txt`. Run `.\scripts\Set-NestedVirtualisation.ps1 -Mode Check | Tee-Object check-before.txt`
   > to save it while it prints, then move the file into `portfolio\evidence\01-prepare-the-workstation\`.

   > **Beginner tip:** Read the script before you run it with `-Mode Disable`:
   > `code .\scripts\Set-NestedVirtualisation.ps1`. Look for what it changes (Windows features, boot
   > settings, registry values). You do not need to understand every line.

3. Actually disable the Windows features that interfere with nested virtualisation:

   ```powershell
   .\scripts\Set-NestedVirtualisation.ps1 -Mode Disable
   ```

   Read the warning, then type `YES` when prompted. The script saves the original settings so they can be
   restored later. It disables Hyper-V-related Windows features, Virtualisation-Based Security, Memory
   Integrity and Credential Guard; running it without `-Mode Disable` only checks the current state.

4. **Restart Windows** when the script finishes. Then, in a new elevated PowerShell window in the same
   folder, verify the settings:

   ```powershell
   .\scripts\Set-NestedVirtualisation.ps1 -Mode Check
   ```

   > **Stop and check:** Continue only when the result says `READY`. In the report, Virtualization-based
   > security should be `Off`, and `Hypervisor running under Windows` should be `False`. If it says
   > `NOT READY`, do not continue to the Proxmox setup. If a policy is listed, capture the report and ask
   > your lecturer; policy-controlled settings must be changed by the school's administrator.

   If Windows still reports Virtualization-based security as enabled or running, and no policy is listed,
   the machine may have a firmware-backed VBS lock. Have the BitLocker recovery key available, remain at the
   computer during restart, then run:

   ```powershell
   .\scripts\Set-NestedVirtualisation.ps1 -Mode Disable -UnlockFirmware
   ```

   Confirm the additional warning. Restart and accept the firmware change at the pre-Windows prompt. If no
   prompt appears, or the check still reports `NOT READY`, stop and ask your lecturer; do not keep repeating
   the firmware-unlock step.

   > **Careful:** The firmware prompt appears _before_ Windows loads and asks you to press a key to accept.
   > If you miss it, nothing changes. Do not repeat it more than once without help.

5. Confirm hardware virtualisation is enabled in the firmware (Task Manager > Performance > CPU >
   "Virtualization: Enabled"). This is separate from the Windows settings changed by the script.
6. In VMware Workstation, create a **LAN Segment** named exactly `LAN-LAB`. VMware creates LAN Segments from
   a VM's settings, so you will do this for real when you create your first VM in the next guide: open
   **VM > Settings > Network Adapter**, choose **LAN segment**, click **LAN Segments...** and **Add**. If
   your lecturer has already set this up, check the segment exists instead of creating a second one.

   > **What's going on:** A LAN Segment is a private virtual network cable that only VMs can plug into.
   > Your Windows PC is _not_ on it, which is the point: the lab is isolated. It also means you cannot reach
   > lab machines from Windows directly. Later guides use `admin01` as the window into the lab.

7. Note which of your workstation's two NICs is for the internet and which is for the lab; you will choose
   the internet one for VMware's NAT network in the next guide.

To restore the Windows settings saved before preparation, run
`.\scripts\Set-NestedVirtualisation.ps1 -Mode Restore` from an elevated PowerShell window, then restart.
Restore returns the saved Windows settings; it does not reinstate a firmware lock removed by the optional
unlock step.

## Check it worked

- The script's post-restart check reports `READY`.
- Task Manager shows hardware virtualization enabled.
- The LAN Segment `LAN-LAB` exists in VMware (you can confirm this properly in the next guide, when a VM
  uses it).

## Evidence to capture

Save these in `portfolio/evidence/01-prepare-the-workstation/`:

| File                              | What it shows                                                                      |
| --------------------------------- | ---------------------------------------------------------------------------------- |
| `check-before.txt`                | The script's report before any change                                              |
| `check-after.txt`                 | The report after the restart, ending in `READY`                                    |
| `task-manager-virtualization.png` | Task Manager > Performance > CPU, showing "Virtualization: Enabled"                |
| `lan-lab.png`                     | The `LAN-LAB` segment in VMware's LAN Segments list (take this when you create it) |
| `evidence.md`                     | Your filled-in evidence log                                                        |

## Explain it in your own words

1. Why does Windows' own security feature stop Proxmox from running fast inside VMware?
2. Which protections did you turn off, what could that expose on a normal PC, and why is that acceptable
   for this one?

## If it goes wrong

- The script reports `NOT READY`: follow the report's yellow lines and ask your lecturer if a policy or
  firmware lock is preventing the change. If it reports VBS as enabled/running with no policy listed,
  follow the optional firmware-unlock step above. Do not rely on only turning off Memory Integrity in
  Windows Security; other Windows hypervisor features may still be active.
- Proxmox later refuses to start a nested guest, or is extremely slow: confirm this guide's script check
  still reports `READY`, hardware virtualisation is enabled in firmware, and nested virtualisation is
  enabled for the Proxmox VM in VMware (guide 03).
- "Running scripts is disabled on this system": you skipped the `Set-ExecutionPolicy` line, or you are not
  in a PowerShell window you opened yourself. Run step 1 again.
- No LAN Segment option: your VMware Workstation edition or version may differ. Ask your lecturer; do not
  create a different kind of network and carry on, because later guides depend on a private segment.
