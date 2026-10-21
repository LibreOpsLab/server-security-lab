# Windows 11 (optional)

Two scripts, run on `win-client01` after it is built from media:

1. `Optimize-LabWindows.ps1` disables telemetry, diagnostics, Copilot and Recall, turns off Widgets and
   consumer features, and removes the OneDrive sync client. Run with `-WhatIf` first to see what it would
   change, then without it. It logs every change to `%ProgramData%\lab\optimize-windows.log` and is safe to
   run again.
2. `Join-LabDomain.ps1 -RootCaPath <path to lab-root-ca.crt>` trusts the lab CA, then joins `lab.internal`.
   It asks for domain administrator credentials interactively; it never takes a password as an argument.

**Status: unverified.** These scripts have been written and reviewed, but not run against a real Windows 11
install (there is no Windows interpreter available in this repository's build environment). Report back
with what worked and what needed changing: see `CONTRIBUTING.md`.
