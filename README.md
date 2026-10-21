# server-security-lab

The student build repo for Advanced Server Security (ICTNWK540 + ICTNWK546). You fork it, build your
lab from it week by week, and push your work to your own fork. **The repo is the lab:** VMs are
disposable, the fork is not.

## Test only your own lab

Every attack and scan in this repo runs against **your own lab guests and nothing else**. Write your
scope first (`weeks/12-baseline-attack/scope.txt.example`); the tools refuse any target outside it.
Never test anything you do not own or have written permission to test.

## What is in here

| Folder       | Owner    | Purpose                                                        |
| ------------ | -------- | -------------------------------------------------------------- |
| `docs/`      | upstream | Git workflow, attack set, troubleshooting                      |
| `scaffold/`  | upstream | The `sslab` tool that writes and compares reports              |
| `weeks/`     | upstream | Steps, starter files with TODOs, and a `check.sh` for each week |
| `build/`     | you      | Your finished work: inventory, playbooks, compose files, configs |
| `portfolio/` | you      | Your AT2 evidence: generated reports and your reflection       |

Upstream owns `docs/`, `scaffold/` and `weeks/`; you own `build/` and `portfolio/`. Pulling upstream
then rarely conflicts. If you edit an upstream file you will meet a merge conflict, which is a
deliberate exercise (see `docs/git-workflow.md`).

## The loop

Attack and audit your lab as built (week 12), harden it (week 15), attack and audit it again with the
same tools (week 17), compare, and reflect. Reports are generated and timestamped in
`portfolio/reports/`. You are marked on what changed and what you understood about it, not on a score.

## Run the tool

```bash
cd scaffold
python -m sslab --help
python -m pytest
```
