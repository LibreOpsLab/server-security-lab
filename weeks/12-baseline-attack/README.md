# Week 12: attack your lab as built

You have a working platform. This week you find out how weak it is, before you change anything. The
threat model you write at the start of this week says what _should_ go wrong; the run shows what _does_.

**Your lab only.** The tools refuse any target outside the ranges you write in your scope file. Never test
anything you do not own or have written permission to test.

> **What's going on:** Up to now you have been a builder. This week you become the person trying to break
> in, using the same open-source tools real testers use. You are not trying to "win". You are collecting
> evidence of how the lab looks to an outsider *before* any hardening, so that in week 17 the difference is
> measurable. If you change anything on the lab while measuring, the comparison is spoiled.

> **Careful:** Attacks can crash services and fill logs. Take the snapshot in step 1 first, run only the
> tools this guide names, and never point them at an address that is not on your own `LAN-LAB`. Running
> these tools against your school's network, a classmate's lab without their written agreement, or the
> internet can break the rules of your course and the law.

## Before you start

- `make verify` was clean in guide 18, and your `lab-verified` snapshots exist.
- You know what each service in your lab does (your guide 07 to 16 evidence says so).
- Time: expect 4 to 6 hours across the week, much of it waiting for scans.

## Steps

1. **Snapshot first.** In VMware (and Proxmox for the guests inside it) take a snapshot named
   `pre-security-baseline` of every VM. If you need to repeat this run later, restore it.
2. **Write your threat model before you attack.** Copy `portfolio/templates/threat-model.md` to
   `portfolio/threat-model.md` and fill in the first three sections: what you are protecting, who might
   attack, and **your predictions** for each guest. Commit it **now**, before any scan. The commit
   timestamp proves you predicted first.
3. **Write your scope.** Copy `scope.txt.example` to `portfolio/scope.txt` and list your lab ranges.

   > **What's going on:** The scope file is your written authorisation. Real testers never start without
   > one: it says exactly which addresses they may touch. The tool refuses to send a packet to anything not
   > listed.

4. **Say who you are.** Create `portfolio/student.toml`:

   ```toml
   student = "Your Name"
   fork = "yourname/server-security-lab"   # your private copy
   ```

5. **Install the tools on `admin01`** (all open source):

   ```bash
   sudo apt install -y nmap hydra curl smbclient
   ```

   Lynis is installed on each Linux guest you audit (`ssh root@<guest> 'apt install -y lynis'`). Do one
   guest first, check it works, then the rest.

   > **Beginner tip:** *nmap* maps which doors (ports) are open on a machine. *hydra* guesses passwords at
   > a login. *Lynis* audits a Linux machine's own settings from the inside. *curl* fetches web pages so you
   > can read their headers. *smbclient* lists and opens Windows file shares.

6. **Run the check** for each host, from the repo root:

   ```bash
   weeks/12-baseline-attack/check.sh docker01 samba-dc01
   TOOLS=windows weeks/12-baseline-attack/check.sh win-client01
   ```

   > **Beginner tip:** Reports land in `portfolio/reports/`. Open the Markdown one in VS Code's preview
   > (`Ctrl+Shift+V`). Read the summary first; the findings are grouped by layer (network, host, service,
   > identity).

7. **Commit the reports** in `portfolio/reports/` without editing them. They carry your name and a
   timestamp; editing them would make them worthless as evidence.
8. **Brief the manager.** Run
   `PYTHONPATH=scaffold python3 -m sslab impact --before <your default report> --after <same report> --out portfolio/reports`
   to get a blank impact table (use the same file for both --before and --after here; the first
   conversation is about the baseline alone). Fill it in, copy `portfolio/templates/manager-briefing.md` to
   `portfolio/manager-briefing-1.md` and write it, then have the conversation with your instructor.
9. **Read your own results.** For each finding, complete the last section of your threat model: was it
   predicted? What would an attacker do with it?
10. **Build your risk register.** Copy `portfolio/templates/risk-register.md` to
    `portfolio/risk-register.md` and decide which findings you will fix, reduce or accept in week 15.

## Optional: attack each other

If time allows, pair up. One of you runs Kali; attack your partner's lab and they attack yours. Both
partners agree first, each writes the other's range into their own scope file, and nothing else is touched.
This is a stretch, not part of the evidence.

## Evidence to capture

| Where | What it shows |
| --- | --- |
| `portfolio/threat-model.md` (committed **before** the scans) | Your predictions |
| `portfolio/scope.txt`, `portfolio/student.toml` | Your authorisation and identity |
| `portfolio/reports/` (`default` reports, unedited) | The audit, nmap and attack-set results for every host |
| `portfolio/threat-model.md` (completed) | Which findings you predicted and what they would let an attacker do |
| `portfolio/manager-briefing-1.md` | Your plain-language briefing note |
| `portfolio/risk-register.md` | The findings you will fix, reduce or accept, and why |
| `portfolio/evidence/12-baseline/evidence.md` | Your evidence log: problems you hit and what surprised you |

## Explain it in your own words

1. Which finding surprised you most, and why had you not predicted it?
2. Explain one finding to a non-technical shop owner in three sentences, with no jargon.

## What you hand in

The `default` reports for every host (audit, nmap and attack set), your threat model with predictions
dated before the first scan, the briefing note, and the first draft of the risk register.

## If it goes wrong

- The tool says a target is outside the scope: check `portfolio/scope.txt` lists the range, written as
  `10.10.10.0/24` (the tool rejects ranges with host bits set, such as `10.10.10.5/24`, on purpose).
- A tool is missing: install it (step 5). A tool that did not run is recorded as `not_run`, never "clean".
- A scan hangs or a service falls over: that is information. Note it, restore the snapshot if needed, and
  say so in your evidence.
- A short name such as `docker01` does not resolve: use the full name (`docker01.lab.internal`) or the
  address from the inventory (`10.10.10.30`). Both must be inside your scope.
- Python errors from `sslab`: you may be in the wrong folder. Run it from the repository root with
  `PYTHONPATH=scaffold`.
