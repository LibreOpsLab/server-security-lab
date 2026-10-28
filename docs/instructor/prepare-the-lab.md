# How to prepare for the lab

For lecturers and technicians getting workstations and software ready **before** students start guide 01.
If you are studying on your own, read [the self-paced section](#studying-on-your-own) first: it tells you
what to download and where to get it, because there is no lecturer to hand it to you.

Allow **half a day** for the first workstation and about **an hour** for each one after that. Do the first
one as a dry run of guide 01 and keep the notes: they become your local fixes.

## What students are given

Students are not expected to find, choose or download installers. The lecturer provides all of this in one
shared place (for example a network share or a USB drive, copied to `D:\iso` on each workstation).

| Item                           | Used in          | Provided as                                        | Notes                                                                                                                                                    |
| ------------------------------ | ---------------- | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **pfSense CE** installer       | Guide 02         | ISO (or the compressed `.iso.gz`; unpack it first) | Download from Netgate. A free account may be needed. Choose the amd64 ISO installer.                                                                     |
| **Proxmox VE 9** installer     | Guide 03         | ISO                                                | From proxmox.com/downloads. PVE 9 is built on Debian 13; use the current 9.x release and note its version.                                               |
| **Debian 13 "trixie" netinst** | Guides 07 and 16 | ISO                                                | From debian.org. Used to hand-build the domain controller and the backup server as VMware VMs. Use the amd64 netinst image.                              |
| **Ubuntu Desktop 26.04 LTS**   | Guide 04         | ISO                                                | From ubuntu.com/download. 26.04 LTS is the current LTS and what the guides and automation assume.                                                        |
| **Windows 11** (optional)      | Guide 17         | ISO or evaluation media                            | Only if your course builds the Windows client. Check your institution's licensing, or use Microsoft's evaluation media. Do not use unofficial downloads. |
| **Kali Linux** (optional)      | Week 12 stretch  | VM image or ISO                                    | Only for the "attack each other" stretch.                                                                                                                |
| **VMware Workstation**         | Guides 01 to 18  | Installer                                          | See [software on the workstation](#software-on-the-workstation).                                                                                         |

You do **not** need to provide: Debian container templates or the Ubuntu cloud image used by the Docker VM.
Proxmox downloads those itself (`pveam`, a cloud image download) through pfSense, as part of `make guests`.
Proxmox Backup Server is installed from Proxmox's own repository onto the Debian 13 VM by `make backup`. This is why `pve01` needs working internet access.

## Workstation requirements

| Requirement | Reference spec                                                      | Why                                                                                                                 |
| ----------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| CPU         | About 10 cores with hardware virtualisation (Intel VT-x or AMD-V)   | Proxmox gets 8 vCPUs                                                                                                |
| RAM         | 32 GB                                                               | The design budgets about 28.5 GB for the VMs, and the Windows host needs the rest                                   |
| Storage     | 512 GB or more of fast storage (NVMe) with at least **350 GB free** | Proxmox 160 GB, backup server 80 GB, then `admin01`, the domain controller, pfSense, optional Windows and snapshots |
| Network     | Two network adapters: one lab, one internet                         | Used by pfSense and the NAT network                                                                                 |
| OS          | Windows 11 with administrator rights for the setup steps            | Guide 01 changes security settings                                                                                  |
| Firmware    | Virtualisation enabled                                              | Guide 01 checks this                                                                                                |

> **Check this before term.** RAM and disk are estimates until measured on a real build (see
> [STATUS.md](../build/STATUS.md)). Do a full build on one workstation of each model and record the real
> figures.

## Software on the workstation

Install these before students arrive. Students install Git, VS Code and Python themselves in
[DevOps 101](../devops-101.md), which is a useful first-week skill, but pre-installing them is fine too.

| Software                            | Notes                                                                                                                                                |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| VMware Workstation                  | Check the current licence terms for your institution before installing. Record the version. Students need to create VMs, LAN Segments and snapshots. |
| Git, VS Code, Python 3.11+          | Via `winget`, as in DevOps 101                                                                                                                       |
| GitHub CLI (optional)               | Handy for private-repo work                                                                                                                          |
| A browser and a PDF/Markdown viewer | Anything current                                                                                                                                     |
| An archive tool                     | Needed if pfSense comes as `.gz`                                                                                                                     |

## Before the first class

Work through this checklist on every workstation.

1. **Hardware virtualisation is on in the firmware.** Task Manager > Performance > CPU shows
   "Virtualization: Enabled".
2. **Windows security features.** Run `.\scripts\Set-NestedVirtualisation.ps1 -Mode Check` from an elevated
   PowerShell in a clone of the repository.
   - If any are enabled by **policy** (group policy or device management), the student cannot turn them off.
     Ask your administrator to exempt the lab PCs, or change the policy.
   - If the firmware-backed VBS lock is set, the script's `-UnlockFirmware` option exists. Test it on one
     PC first, and have BitLocker recovery keys ready.
3. **Admin rights.** Students need to run PowerShell as administrator for guide 01 only, and to run VMware.
4. **Free disk space**: at least 350 GB free on the drive that will hold the VMs.
5. **Network adapters.** Confirm there are two, and that the internet one gets a working connection.
6. **Internet access from the lab VMs.** pfSense's NAT path needs outbound web and DNS (and NTP, if allowed).
   If your institution's firewall restricts this, request access to: Debian and Ubuntu package mirrors,
   `download.proxmox.com`, GitHub, `docker.io` and `ghcr.io` (container images), and Grafana's package
   repository.
7. **ISOs are in place** and **checksums match** (below).
8. **A private repository per student** exists and the student has access (see
   [Git workflow](../git-workflow.md)). Decide how repos are created: one per student from a template, or
   students run `scripts/create-private-copy.sh`.
9. **Do the dry run.** Build guides 01 to 04 on one workstation. Take notes and screenshots of anything that
   differs from the guides.

### Verify the ISOs

Download each ISO from the vendor's own site, copy the **published checksum** from the same page, and
compare it. A mismatch means a corrupted or tampered download.

```powershell
Get-FileHash D:\iso\ubuntu-26.04-desktop-amd64.iso -Algorithm SHA256
```

Put a `CHECKSUMS.txt` beside the ISOs listing each file, its source URL, the date downloaded, and its SHA-256.
Students can then repeat the check, and it makes a good tiny evidence item for guide 01.

> **Do not commit ISOs to the repository.** They are large, and the repository is copied to every student.
> Keep them in a shared location.

## Shared accounts and secrets

- Students create their own passwords during installs. Tell them to keep them out of Git
  ([welcome guide](../build/00-welcome.md)).
- The lab's _starting_ user passwords are in `lab/data/users.csv` and are weak on purpose (see
  [weak defaults](../instructor-weak-defaults.md)). That is not a secret and not a mistake.
- Never share an instructor's own credentials, API tokens or recovery keys in the lab images or the repo.

## Lecturer-built images (if you choose them)

If you decide to give students ready-made copies of the hardest guests, build them once and treat the
exported files like ISOs: stored centrally, checksummed, and not in Git. Record exactly which guide steps
they replace, so the student still learns what the step does (even if they don't run it). See
[STATUS.md](../build/STATUS.md) for the risk list that motivates this.

## Studying on your own

You do not have a lecturer, so you have to gather what a lecturer would normally hand you. It costs nothing
but time and disk space.

1. **Check your computer first.** You need roughly the [workstation specification](#workstation-requirements)
   above: 32 GB of RAM is the realistic minimum for the full build, and about 350 GB free disk. With 16 GB
   you can build a smaller version (skip the Docker apps, monitoring, mail and Windows), but the guides
   assume the full lab, so you will have to adapt memory sizes in `lab/inventory/group_vars/all.yml`.
2. **Get the software** in the lists above, from the vendors' own websites:
   VMware Workstation (check its current licence for personal use), pfSense CE, Proxmox VE and Ubuntu
   Desktop 26.04 LTS. Windows 11 and Kali are optional.
3. **Verify the checksums** exactly as above.
4. **Use your own private repo.** You do not have a lecturer's repository, so follow the self-study quick
   start in the [README](../../README.md) to make your own private copy.
5. **Skip the lecturer-only steps.** Where a guide says "ask your lecturer", use the lab issue tracker
   (see [CONTRIBUTING.md](../../CONTRIBUTING.md)), or write down what you tried. Keep your evidence folders
   anyway: they prove your own learning and make a good portfolio.
6. **Plan your time.** Use the [week map](../build/WEEK-MAP.md) as a pace guide, not a deadline. Expect 35 to
   50 hours for the build, so about 4 to 5 hours a week for 11 weeks.
7. **Security and licensing.** Only use software you are licensed to use, and only attack your own lab.
   Guide 01 changes security settings on the host computer: do it only on a machine you own and understand.
   Turning off Windows protections on your everyday laptop is a real risk. If you can, use a spare PC or a
   dual-boot disk.

## After the first cohort

- Update the version table here with the actual ISO versions you used.
- Record the real RAM and disk figures in `lab/inventory/group_vars/all.yml` and in
  [STATUS.md](../build/STATUS.md).
- Turn the recurring student problems into "If it goes wrong" entries in the relevant guides.
