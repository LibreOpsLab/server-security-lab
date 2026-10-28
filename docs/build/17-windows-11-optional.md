# 17: Windows 11 (optional)

## What you will build

`win-client01`, with telemetry, diagnostics, Copilot and Recall disabled, and joined to the lab domain.

**Time and difficulty:** 2 to 4 hours. Medium to hard. Optional, and the scripts are **unverified** (see
below). Choose this if your course's security weeks need a Windows target.

## Why

This guest is optional because it adds real RAM cost; build it if your course's security weeks need a
Windows target, or skip it and `make verify` will report it as skipped rather than failed.

> **What's going on:** Real offices run mostly Windows desktops, and attackers target them first. A Windows
> client on the domain lets you see how identity (guide 07) reaches a desktop. The first script removes
> consumer features and tracking so the machine is a quiet, predictable target. The second joins it to the
> domain, so staff sign in with their lab accounts.

> **Careful:** Windows 11 needs 4 GB of the workstation's RAM while it runs. If the lab starts to swap
> (everything slows and the disk light stays on), shut it down while you work on other guides.

## Before you start

- Guides 07 and 08 are complete.
- Ask your lecturer for the approved Windows 11 media and licensing. Do not download from unofficial
  sources.
- Take a snapshot of the new VM before running either script.

## Steps

1. Install Windows 11 from media, static address `10.10.10.11/24`, DNS `10.10.10.21`. Put the VM on
   `LAN-LAB`.
2. Copy `lab/windows/` and `lab/secrets/ca/root/certs/ca.cert.pem` to the guest. (Only the public
   certificate file; never copy anything else from `lab/secrets/`.)
3. From an elevated PowerShell prompt:

   ```powershell
   .\Optimize-LabWindows.ps1 -WhatIf   # see what it would change first
   .\Optimize-LabWindows.ps1
   .\Join-LabDomain.ps1 -RootCaPath .\ca.cert.pem
   ```

   > **Beginner tip:** `-WhatIf` is a PowerShell habit worth keeping: it prints what a command *would* do
   > without doing it. Read that list first, and keep a copy for your evidence.

   > **What's going on:** The domain join prompts for domain administrator credentials. It never takes a
   > password as an argument, so the password does not end up in your command history.

## Check it worked

- `Get-Service DiagTrack` shows `Disabled`.
- The machine appears in `samba-tool computer list` on `samba-dc01` after the join and restart.
- You can sign in at the Windows sign-in screen as a lab user, such as `LAB\alice`.

## Evidence to capture

Save in `portfolio/evidence/17-windows-11-optional/`:

| File | What it shows |
| --- | --- |
| `whatif.txt` | Output of the `-WhatIf` run |
| `optimize-log.txt` | A copy of `%ProgramData%\lab\optimize-windows.log` |
| `diagtrack.txt` | `Get-Service DiagTrack` output |
| `computer-list.txt` | `samba-tool computer list` on the DC including `win-client01` |
| `domain-login.png` | The Windows desktop signed in as a lab user |
| `evidence.md` | Your filled-in evidence log (or a note that you skipped this guide and why) |

## Explain it in your own words

1. Pick two things the script turned off. Why would a business want them off, and what does it lose?
2. What happens, from the user's point of view, when a Windows PC joins the domain?

## If it goes wrong

- **Status: unverified.** These scripts have been reviewed but not run on a real Windows 11 install in this
  project. If a step fails or a setting does not stick, please report it (see `CONTRIBUTING.md`) with the
  exact error. That report is itself good evidence.
- The join fails with "domain not found": the VM's DNS must be `10.10.10.21` (the domain controller).
- The join fails with a time error: Windows' clock must be within a few minutes of the DC's.
