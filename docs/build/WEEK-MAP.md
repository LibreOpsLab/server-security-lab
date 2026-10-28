# Week map: a 20-week course

A suggested plan for a 20-week Diploma unit with about **4 to 5 lab hours a week** plus some self-directed
time. Adjust freely: nothing in the repo depends on this file, it just saves re-deriving the order each time.

Weeks 1 to 11 **build** the lab. Weeks 12 to 20 **attack, harden, re-attack and explain** it. The build has
two catch-up weeks so that one stuck student does not lose the second half of the course.

> **Why the order is not 01, 02, 03...** Your Windows PC cannot see the private lab network, so you build
> `admin01` first (guide 04, Part A) and use it to configure pfSense. Single sign-on (11) comes before the
> apps (10) because the apps need the sign-in portal. Monitoring (15) comes after the apps because Grafana is
> served through the Docker VM's reverse proxy.

Lecturers: see [How to prepare for the lab](../instructor/prepare-the-lab.md) before week 1.

## The plan

| Week | Do                                                                                                                       | You finish with                                                      | Evidence folder(s)     |
| ---- | ------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------- | ---------------------- |
| 1    | [DevOps 101](../devops-101.md), [00 Welcome](00-welcome.md), [01 Prepare the workstation](01-prepare-the-workstation.md) | Git/VS Code working, nested virtualisation `READY`, `LAN-LAB` exists | `01-*`                 |
| 2    | [04 admin01](04-admin01.md) (Part A), [02 pfSense](02-pfsense.md)                                                        | `admin01` on the lab network, pfSense routing and answering          | `02-*`, `04-*` (part)  |
| 3    | [03 Proxmox](03-proxmox.md), [04 admin01](04-admin01.md) (Part B)                                                        | `pve01` installed, SSH key working from `admin01`                    | `03-*`, `04-*`         |
| 4    | [05 Repo, inventory and secrets](05-the-repo-inventory-and-secrets.md), [06 Create the guests](06-create-the-guests.md)  | All eight guests created and reachable, secrets backed up            | `05-*`, `06-*`         |
| 5    | [07 Identity](07-identity.md)                                                                                            | Samba AD running, staff accounts loaded                              | `07-*`                 |
| 6    | [08 DNS, DHCP and time](08-dns-dhcp-and-time.md), [09 Squid](09-squid.md)                                                | Name, address and time checks pass; proxy blocks a test site         | `08-*`, `09-*`         |
| 7    | [11 Single sign-on](11-single-sign-on.md), [10 Docker VM and apps](10-docker-vm-and-apps.md)                             | Portal works with a second factor; three apps behind it              | `10-*`, `11-*`         |
| 8    | [12 Mail](12-mail.md)                                                                                                    | A test email delivered between two lab users                         | `12-*`                 |
| 9    | [13 File transfer and shares](13-file-transfer-and-shares.md), [14 Wi-Fi: RADIUS](14-wifi-radius.md)                     | Shares and SFTP work; one EAP `SUCCESS` and one reject               | `13-*`, `14-*`         |
| 10   | [15 Monitoring and logs](15-monitoring-and-logs.md), [16 Backup and restore](16-backup-and-restore.md)                   | Dashboard and alert; a proven restore                                | `15-*`, `16-*`         |
| 11   | [17 Windows 11](17-windows-11-optional.md) (optional), [18 Verify](18-verify.md), **catch-up**                           | `make verify` clean; `lab-verified` snapshots                        | `17-*`, `18-*`         |
| 12   | [Week 12: baseline attack](../../weeks/12-baseline-attack/README.md)                                                     | Threat model, scope, default reports                                 | `portfolio/reports/`   |
| 13   | Impact table, [manager conversation 1](../instructor/manager-conversation.md), risk register                             | Briefing note 1; risk register from the findings                     | `portfolio/`           |
| 14   | **Catch-up** and hardening plan                                                                                          | `build/hardening-notes.md`: findings you will close, and why         | `build/`               |
| 15   | [Week 15: harden](../../weeks/15-harden/README.md) (part 1)                                                              | Network and host controls written as code and tested on a clone      | `build/`               |
| 16   | [Week 15: harden](../../weeks/15-harden/README.md) (part 2)                                                              | Service and identity controls; `hardened` reports                    | `portfolio/reports/`   |
| 17   | [Week 17: re-attack and compare](../../weeks/17-reattack-compare/README.md)                                              | Comparison reports                                                   | `portfolio/reports/`   |
| 18   | Remediate what is still open; re-run the comparison                                                                      | Final comparison with notes on accepted gaps                         | `build/`, `portfolio/` |
| 19   | Manager conversation 2; finish the reflection                                                                            | Briefing note 2, `reflection.md`                                     | `portfolio/`           |
| 20   | Portfolio review and submission; **catch-up**                                                                            | Everything committed and tagged                                      | whole `portfolio/`     |

A lab is a lot of work for a first-time builder. Realistic effort for the build is about **35 to 50 hours**
in total, so the in-class hours alone will not always be enough. These figures are estimates until a student
cohort has built it (see [STATUS.md](STATUS.md)).

## When someone falls behind

Do not let a student skip the whole build. The security weeks need these services to attack. Use this
priority order:

| Priority                                | Guides                             | Why                                                                                                                                                  |
| --------------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Core: everyone builds these**         | 01 to 08, 10, 11, 12, 13, 18       | The attack set targets SSH on several guests, the web tier on `docker01`, mail on `mail01` and the shares on `files01`. Identity underpins them all. |
| **Strongly recommended**                | 09 Squid, 15 Monitoring            | Squid is quick. Monitoring lets students see "did anything notice?" during the attacks.                                                              |
| **Stretch: can be cut or demonstrated** | 14 Wi-Fi, 16 Backup, 17 Windows 11 | Harder or heavier, and the attack set does not depend on them. The lecturer can show these once, and students write up what they saw.                |

If a core guide will not work on a student's workstation after the 20-minute rule and a lecturer visit,
**record the failure as evidence and have the lecturer set up a ready-made copy**. A student who has
honestly documented where and why they were stuck has still shown the skills this unit is about.

## Checkpoints the lecturer can mark

| By end of week | Check       | What to look at                                              |
| -------------- | ----------- | ------------------------------------------------------------ |
| 3              | Foundations | Evidence folders 01 to 04 complete; `pve01` reachable        |
| 6              | Identity    | Folders 05 to 09 complete; `ldapsearch` and `chronyc` output |
| 9              | Services    | Folders 10 to 14; student can explain the sign-in flow       |
| 11             | Working lab | Folder 18: clean `make verify`, fix log, snapshots           |
| 13             | Baseline    | Default reports, impact table, briefing note 1               |
| 17             | Comparison  | `hardened` reports and comparison reports                    |
| 20             | Portfolio   | Reflection, briefing note 2, whole repo committed            |

Weeks 12, 15 and 17 are the measure, harden, re-measure loop; see
[docs/how-it-works.md](../how-it-works.md) and `weeks/` for that part of the course.
