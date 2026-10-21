# Instructor guide: what "default" leaves open, and the lab validation

Status: **draft, unverified.** Written before the lab validation. Every row is a candidate until it has been
built and scanned on a real lab workstation (checklist at the end). Contributions that verify a row are very welcome (see CONTRIBUTING.md). Nothing in this list is a planted
trick: each is how the software behaves out of the box, or how a normal how-to build leaves it.

"Default" in this unit means _functional but not secure_: built to the student's design, every service
working, nothing hardened. A vendor-default install is not a usable platform.

## Candidate weak defaults

These are now built, not just planned: each row names the Ansible role or template that leaves the default
in place. Still **unverified** on a real lab until the first build (`docs/build/STATUS.md`).

| Where                        | What is open by default                                                                                | Left by (role/template)                 | Found by                | Closed in |
| ----------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------- | ----------------------- | --------- |
| Linux hosts (SSH)             | Password login on; no lockout, short lab passwords accepted                                            | `baseline`, `samba_dc` (password policy) | Lynis, `ssh-weak-creds` | Week 15   |
| Lab accounts                  | `lab/data/users.csv` gives most staff one shared password; two accounts (`test`, `user`) use a weaker one | `samba_dc` (`load-users.sh`)             | `ssh-weak-creds`        | Week 15   |
| Web tier (Traefik/NextCloud)  | No HSTS, CSP, X-Frame-Options or nosniff; server banners visible                                       | `docker_host` (`dynamic.yml.j2`)         | `web-basics`, nmap      | Week 15   |
| Postfix                       | `VRFY` enabled; relaying allowed for the whole lab subnet                                               | `mail` (`main.cf.j2`)                    | `mail-basics`           | Week 15   |
| Samba file server             | A "notices" share with `guest ok = yes`                                                                | `files_server` (`smb.conf.j2`)           | `anon-directory`        | Week 15   |
| pfSense                       | Default "allow LAN to any" firewall rule                                                               | `lab/pfsense/config.xml.j2`              | `enum-services`, review | Week 15   |
| Docker socket                 | Traefik can read the Docker socket, close to root access on `docker01`                                 | `docker_host` (Traefik compose)          | student review          | Week 15   |
| Monitoring and logs           | Loki and Alloy's metrics port accept anyone on the LAN with no login                                   | `monitoring`, `log_shipper`              | `enum-services`         | Week 15   |
| Windows 11 (if built)         | No account lockout, default audit policy, firewall profiles as installed                               | (built by hand; no Ansible role)         | Windows audit           | Week 15   |
| Updates                       | No automatic security updates configured on any guest                                                  | `baseline` (deliberately omitted)        | Lynis                   | Week 15   |
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
