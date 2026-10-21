# 17: Windows 11 (optional)

## What you will build

`win-client01`, with telemetry, diagnostics, Copilot and Recall disabled, and joined to the lab domain.

## Why

This guest is optional because it adds real RAM cost; build it if your course's security weeks need a
Windows target, or skip it and `make verify` will report it as skipped rather than failed.

## Steps

1. Install Windows 11 from media, static address `10.10.10.11/24`, DNS `10.10.10.21`.
2. Copy `lab/windows/` and `lab/secrets/ca/root/certs/ca.cert.pem` to the guest.
3. From an elevated PowerShell prompt:

   ```powershell
   .\Optimize-LabWindows.ps1 -WhatIf   # see what it would change first
   .\Optimize-LabWindows.ps1
   .\Join-LabDomain.ps1 -RootCaPath .\ca.cert.pem
   ```

## Check it worked

- `Get-Service DiagTrack` shows `Disabled`.
- The machine appears in `samba-tool computer list` on `samba-dc01` after the join and restart.

## If it goes wrong

- **Status: unverified.** These scripts have been reviewed but not run on a real Windows 11 install in this
  project. If a step fails or a setting does not stick, please report it (see `CONTRIBUTING.md`) with the
  exact error.
