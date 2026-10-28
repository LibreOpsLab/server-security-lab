# Build status

Status of every component. Everything here is **unverified** until it has been built on a real lab
workstation and ticked off against [18-verify.md](../build/18-verify.md). Contributions that verify a
row are very welcome; see [CONTRIBUTING.md](../../CONTRIBUTING.md).

| Guest                               | Role       | Status     |
| ----------------------------------- | ---------- | ---------- |
| `pfsense01`                         | firewall   | unverified |
| `pve01`                             | hypervisor | unverified |
| `admin01`                           | admin      | unverified |
| `win-client01` (optional)           | client     | unverified |
| `samba-dc01` (Debian 13 VM, VMware) | samba_dc   | unverified |
| `auth01`                            | auth       | unverified |
| `radius01`                          | radius     | unverified |
| `mon01`                             | monitoring | unverified |
| `mail01`                            | mail       | unverified |
| `files01`                           | files      | unverified |
| `pbs01` (Debian 13 VM, VMware)      | backup     | unverified |
| `docker01`                          | docker     | unverified |

## Tooling

| Component                        | Status                                                                         |
| -------------------------------- | ------------------------------------------------------------------------------ |
| `sslab` (audit, attack, compare) | tested against hand-written sample output, unverified against real tool output |
| Lab build roles and scripts      | tested statically (lint, syntax, compose config); unverified on a real build   |
| Windows 11 scripts               | unverified (no PowerShell interpreter available to the author)                 |

## Course readiness (reviewed 2026-10-28)

Is this ready to put in front of a class of Diploma students? **Not yet.** The content, structure and
teaching support are in good shape. The one thing missing is a full end-to-end build by a person. Treat that
as the gate before term starts.

### What is in place

- Build guides 00 to 18, each with a time estimate, plain-language explanations, a check, an _Evidence to
  capture_ table, questions to answer in the student's own words, and troubleshooting.
- A [20-week map](WEEK-MAP.md), with two catch-up weeks in the build, a "core versus stretch" list for
  students who fall behind, and lecturer checkpoints.
- An evidence system (`portfolio/evidence/`, [evidence log template](../../portfolio/templates/evidence-log.md))
  and [glossary](../glossary.md).
- Static checks pass for the docs and wiring tests; the Ansible roles were linted and syntax-checked by the
  author.

### What is still risky (do these before term)

| Risk                                                                    | Why it matters                                                                                                                                                         | What to do                                                                                                                                       |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **No full build has ever been done**                                    | Every component is unverified. Expect several fixes in the first run.                                                                                                  | A lecturer or technician builds the whole lab from the guides on a lab PC, following them literally, and files fixes. Budget 2 to 3 days.        |
| **Samba AD on a Debian 13 VM, PBS on a Debian 13 VM, PEAP via winbind** | The two VMs replace the earlier container layout, which removes the biggest risk; PEAP via winbind is still the hardest service.                                       | Build the DC and PBS VMs first in the dry run, then RADIUS.                                                                                      |
| **Nested virtualisation depends on firmware, VBS and policy**           | If it cannot be switched on, Proxmox is unusable.                                                                                                                      | Test on every model of lab PC. Some may need an administrator's policy change or the firmware step.                                              |
| **Memory budget is an estimate** (about 28.5 GB of 32)                  | A tight budget plus Windows 11 may swap and feel broken.                                                                                                               | Measure real use after the first build; update `ram_budget_mb` in the inventory.                                                                 |
| **Total effort is 35 to 50 hours for beginners**                        | In-class time alone may not be enough.                                                                                                                                 | Confirm self-study hours with the course plan, or pre-build the hardest guests (`samba-dc01`, `radius01`, `pbs01`) as a lecturer-provided image. |
| **Windows 11 scripts have never been run**                              | Windows is optional here, but the Windows audit in the security weeks needs a target.                                                                                  | Run them once on a test VM before term.                                                                                                          |
| **`sslab` parsers tested only against hand-written output**             | Real Lynis, nmap and hydra output may break them in week 12.                                                                                                           | Complete the validation checklist in [instructor-weak-defaults.md](../instructor-weak-defaults.md).                                              |
| **Tests on Windows**                                                    | The Python tests that run shell scripts fail on a Windows host (about 49 failed, 7 errors on a clean Windows checkout, since they need `bash`, `openssl` and friends). | Run the tests on Linux or in CI. This does not affect students on `admin01`.                                                                     |

### Changes made in this review

- **Build order.** Guide 02 (pfSense) previously needed a browser on the lab network, which does not exist
  until `admin01` is built. `admin01` is now built in two parts (A before pfSense, B after Proxmox).
- **Per-service make targets.** `make services` built four unrelated servers at once, while guides 11 to 14
  presented them one per week. Added `make sso`, `make mail`, `make files`, `make radius` (tags in
  `40-services.yml`). Plain `make services` still builds all four.
- **SSO before apps.** The apps need the sign-in portal; monitoring needs the apps (Grafana is served
  through Traefik). Guide order and the week map now reflect that.
- **`make baseline` was never mentioned** in any guide. It is now part of guide 06.
- **SSH key.** `ssh root@10.10.10.5` would not use `~/.ssh/lab_admin` without configuration. Guide 04 adds
  an SSH config entry.
- **`eapol_test`** was never installed on `admin01`. Guide 14 installs it and copies the config.
- **Scope example** pointed at `10.10.0.0/24`, not the lab's `10.10.10.0/24`, so the tools would refuse every
  lab target. Fixed.
- **Missing templates**: the threat model and risk register mentioned in week 12 did not exist. Added.
- Fixed a broken link in guide 08 and duplicate step numbering in guide 04.

### Still to decide

- Whether to add a lecturer-built image for the hardest guests, to protect the second half of the course.
- Whether the briefing and reflection need a marking guide (rubric) for assessors.
- Whether to add a short screencast for guides 02 and 03, where first-time builders usually stall.

### Versions (updated 2026-10-28)

Everything was moved to current releases. These were checked against the vendors' release pages on that date;
none has been run on a real build.

| Component                   | Version                              | Notes                                                                           |
| --------------------------- | ------------------------------------ | ------------------------------------------------------------------------------- |
| Debian                      | 13 "trixie"                          | LXC containers and the two hand-built VMs (`samba-dc01`, `pbs01`)               |
| Proxmox VE / Backup Server  | 9.x / 4.x                            | PBS installs from the `trixie` repository                                       |
| Ubuntu                      | 26.04 LTS                            | `admin01` desktop, and the cloud image for `docker01`                           |
| Samba, Postfix, Dovecot     | 4.22, 3.10, 2.4 (Debian 13 packages) | Dovecot 2.4 changed its configuration format; the mail role was rewritten       |
| Authelia                    | 4.39.28                              | Package checksum pinned in the role                                             |
| Traefik, NextCloud, MariaDB | 3.7, 33, 11.8 LTS                    |                                                                                 |
| Stirling PDF, Vaultwarden   | 3.2.2, 1.37.4                        | Stirling PDF jumped from 0.46 to 3.x: check its environment settings            |
| pfSense CE                  | current release                      | The rendered `config.xml` was written for an older release; import and check it |

### Risks introduced by the version move

| Risk                                  | Why                                                                                                      | Check                                                  |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Dovecot 2.4 configuration             | Rewritten from the documentation, never run. The role validates it with `doveconf -n` before restarting. | Guide 12                                               |
| NextCloud 33 and the `oidc_login` app | A third-party app may lag a new NextCloud major version                                                  | Guide 10 and 11: sign in to NextCloud through Authelia |
| Stirling PDF 3.x                      | Settings and image changed a lot from 0.46                                                               | Guide 10                                               |
| Authelia checksum                     | Computed from the downloaded release, not from a separately published checksum                           | Compare with the release page                          |
| pfSense config import                 | The template's version stamp is old                                                                      | Guide 02: import, then check interfaces and DHCP       |
| Debian 13 specifics                   | No `rsyslog` by default (logs are in the journal), `nftables` replaces `iptables`                        | Guides 12 to 15 use `journalctl`                       |

### Layout change in this revision

`samba-dc01` and `pbs01` moved from Proxmox containers to Debian 13 VMs in VMware, because the identity system
and the backups should not depend on the hypervisor they serve. Students install Debian by hand and
`lab/bootstrap/prep-guest.sh` finishes it over SSH. New helper scripts: `lab/preflight.sh` (check before a step),
`lab/evidence.sh` (collect evidence after it) and `lab/backup-dc.sh` (the domain controller's own backup).
