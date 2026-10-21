# Instructor guide: what "default" leaves open, and the lab validation

Status: **draft, unverified.** Written before the lab validation. Every row is a candidate until it has been
built and scanned on a real lab workstation (checklist at the end). Contributions that verify a row are very welcome (see CONTRIBUTING.md). Nothing in this list is a planted
trick: each is how the software behaves out of the box, or how a normal how-to build leaves it.

"Default" in this unit means _functional but not secure_: built to the student's design, every service
working, nothing hardened. A vendor-default install is not a usable platform.

## Candidate weak defaults

| Where               | What is open by default                                                                                                                                        | Found by                        | Closed in                          |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ---------------------------------- |
| Linux hosts (SSH)   | Password login on; root login not blocked on some images; weak lab password policy                                                                             | Lynis, `ssh-weak-creds`         | Week 15                            |
| Lab accounts        | Weeks 1-9 use one documented lab password so the build is quick (**decision needed**: it must be on the attack wordlist for `ssh-weak-creds` to find anything) | `ssh-weak-creds`                | Week 15 (second factor, key login) |
| nginx / web         | Version in the `Server` header; no HSTS, CSP, X-Frame-Options or nosniff                                                                                       | `web-basics`, nmap              | Week 15                            |
| Postfix             | `VRFY` enabled (the Postfix default); relaying allowed for the local subnet, which includes `admin01`                                                          | `mail-basics`                   | Week 15                            |
| Samba file server   | A "public notices" share with `guest ok = yes`, as many how-tos create it (**add to the week 7 design**)                                                       | `anon-directory`                | Week 15                            |
| Services            | Unneeded daemons left running after install; cleartext FTP if the legacy SFTP exercise leaves vsftpd on                                                        | `enum-services`, Lynis          | Week 15                            |
| pfSense             | Permissive LAN-to-LAN and LAN-to-firewall rules from the default "allow LAN" rule                                                                              | `enum-services`, student review | Week 15                            |
| Windows 11 / Server | No account lockout, default audit policy, firewall profiles as installed                                                                                       | Windows audit                   | Week 15                            |
| Updates             | No automatic security updates configured                                                                                                                       | Lynis                           | Week 15                            |

The first attack run should produce findings in all four layers (network, host, service, identity). If a
layer is empty after the spike, add the smallest missing real default rather than a contrived hole.

## What a "good" comparison looks like

Not 100 per cent closed. A healthy class result has closed findings in every layer, some findings
**unchanged** that the student can explain (the cost was not worth it, or the design needs it), and at
least one **new** finding the hardening itself introduced (a rule too strict, a service now noisy). Those
last two are where the reflection earns its marks.

## Lab validation checklist (needs a real workstation)

1. Build the lab from the repo on a lab workstation. At the end of the week 11 state, take the
   `pre-security-baseline` snapshot of every VM.
2. Install `nmap`, `hydra`, `curl`, `smbclient` on `admin01`; Lynis on each Linux guest.
3. Record real RAM use on `admin01` with the tools running, alongside the lab (the reference workstation has 32 GB).
4. Run `weeks/12-baseline-attack/check.sh` against every guest. Keep the raw tool output.
5. Replace the placeholder fixtures in `scaffold/tests/fixtures/` with trimmed real output, rerun
   `python -m pytest`, and fix the parsers where reality differs.
6. Choose the Windows audit tool (open source; a HardeningKitty-style CSV is assumed by
   `collectors/windows.py`), set `_WIN_CMD` in `collectors/__init__.py`, and add real output as a fixture.
7. Apply a reference hardening, run `weeks/17-reattack-compare/check.sh`, and confirm the comparison has
   closed findings in every layer and at least one unchanged or new row.
8. Update the table above with what was actually found, and mark each row verified.
9. Decide the lab password convention (see the second row) and the Windows audit command; record both here.
