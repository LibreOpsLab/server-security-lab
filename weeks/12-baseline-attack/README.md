# Week 12: attack your lab as built

You have a working platform. This week you find out how weak it is, before you change anything. The
threat model you wrote this week says what _should_ go wrong; this run shows what _does_.

**Your lab only.** The tools refuse any target outside the ranges you write in your scope file. Never test
anything you do not own or have written permission to test.

## Steps

1. **Snapshot first.** In VMware (and Proxmox for the guests inside it) take a snapshot named
   `pre-security-baseline` of every VM. If you need to repeat this run later, restore it.
2. **Write your scope.** Copy `scope.txt.example` to `portfolio/scope.txt` and list your lab ranges.
3. **Say who you are.** Create `portfolio/student.toml`:

   ```toml
   student = "Your Name"
   fork = "yourname/server-security-lab"   # your private copy
   ```

4. **Install the tools on `admin01`** (all open source): `nmap`, `hydra`, `curl`, `smbclient`. Lynis is
   installed on each Linux guest you audit.
5. **Run the check** for each host, from the repo root:

   ```bash
   weeks/12-baseline-attack/check.sh docker01 samba-dc01
   TOOLS=windows weeks/12-baseline-attack/check.sh win-client01
   ```

6. **Commit the reports** in `portfolio/reports/` without editing them.
6a. **Brief the manager.** Run `python -m sslab impact --before <your default report> --after <same report> --out portfolio/reports` to get a blank impact table (use the same file for both --before and --after here; the first conversation is about the baseline alone). Fill it in, copy `portfolio/templates/manager-briefing.md` to `portfolio/manager-briefing-1.md` and write it, then have the conversation with your instructor.

7. **Read your own results.** For each finding, write one line in your threat model: was it predicted?
   What would an attacker do with it?

## Optional: attack each other

If time allows, pair up. One of you runs Kali; attack your partner's lab and they attack yours. Both
partners agree first, each writes the other's range into their own scope file, and nothing else is touched.
This is a stretch, not part of the evidence.

## What you hand in

The `default` reports for every host (audit, nmap and attack set), and the one-line notes in your threat
model. Next week your risk register is built from these findings.
