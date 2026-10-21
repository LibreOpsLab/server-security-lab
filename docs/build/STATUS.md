# Build status

Status of every component. Everything here is **unverified** until it has been built on a real lab
workstation and ticked off against [18-verify.md](../build/18-verify.md). Contributions that verify a
row are very welcome; see [CONTRIBUTING.md](../../CONTRIBUTING.md).

| Guest | Role | Status |
| --- | --- | --- |
| `pfsense01` | firewall | unverified |
| `pve01` | hypervisor | unverified |
| `admin01` | admin | unverified |
| `win-client01` (optional) | client | unverified |
| `samba-dc01` | samba_dc | unverified |
| `auth01` | auth | unverified |
| `radius01` | radius | unverified |
| `mon01` | monitoring | unverified |
| `mail01` | mail | unverified |
| `files01` | files | unverified |
| `pbs01` | backup | unverified |
| `docker01` | docker | unverified |

## Tooling

| Component | Status |
| --- | --- |
| `sslab` (audit, attack, compare) | tested against hand-written sample output, unverified against real tool output |
| Lab build roles and scripts | tested statically (lint, syntax, compose config); unverified on a real build |
| Windows 11 scripts | unverified (no PowerShell interpreter available to the author) |

