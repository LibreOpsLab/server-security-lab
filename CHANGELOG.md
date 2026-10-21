# Changelog

All notable changes. Learners: read this before merging `upstream/main` into your fork.

## Unreleased

- Initial public version: `sslab` tool (audit, attack, compare), fixed attack set, week guides for the
  baseline attack, hardening and re-attack weeks, reflection template, scope guard.
- Known gap: parsers are tested against hand-written sample output, not yet real tool output.

- `scripts/create-private-copy.sh` makes a private copy that keeps history (GitHub forks of public repos are always public) and adds `upstream`. Reports now label the learner repo "Repository".
- Full lab build ("business in a box"): docs, Ansible roles and scripts for pfSense, Proxmox, Samba AD,
  Authelia SSO, FreeRADIUS, mail, file/SFTP, the Docker apps, monitoring, backup, and optional Windows 11
  debloat and domain join. Unverified on a real workstation; see `docs/build/STATUS.md`.
- `sslab impact`: a blank business-impact table for the manager conversation (`docs/instructor/manager-conversation.md`).
