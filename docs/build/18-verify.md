# 18: Verify your lab

## What you will build

Nothing new: this is where you prove everything from guides 02 to 17 actually works together.

**Time and difficulty:** 1 to 3 hours, depending on how many checks fail. Easy to run; fixing failures is
the real work, and a good place to practise reading error messages.

## Why

A lab you have not checked end to end is a guess. This is the same discipline the security loop asks of you
later: measure, don't assume.

> **What's going on:** `make verify` runs about twenty small tests, one per service. Each does something
> real: asks DNS a question, signs in over LDAP, sends a test email, opens a web page. Each prints exactly
> one line: `PASS`, `FAIL` or `SKIP`. `SKIP` means an optional part is not built, which is fine.

## Before you start

- Everything you plan to build is built. Optional parts (guide 17, a Wi-Fi access point) may be absent.
- All guests are running.
- Take a snapshot of **every** VM and guest called `lab-verified` once the run is clean. This is your
  restore point. Week 12 asks for a second snapshot, `pre-security-baseline`.

## Steps

```bash
cd lab
mkdir -p ../portfolio/evidence/18-verify
make verify 2>&1 | tee ../portfolio/evidence/18-verify/verify-run-1.txt
```

Each line is `PASS`, `FAIL` or `SKIP`. `SKIP` is normal for an optional part you did not build (Windows 11,
a Wi-Fi access point). Any `FAIL` is something to fix before you move on.

1. Run it and save the output. This first run is your "before".
2. For each `FAIL`: read the message, find the guide it names, fix the cause, and run just that check
   again with `./verify/verify.sh --only NAME`.
3. When it is clean, run the whole suite again and save it as `verify-run-final.txt`.

> **Beginner tip:** Keep a table as you go: check name, what failed, what the message said, what you
> changed, whether it then passed. That table is the best single piece of evidence in the whole build.

## Check it worked

The summary line reads `N passed, 0 failed, M skipped`.

## Evidence to capture

Save in `portfolio/evidence/18-verify/`:

| File | What it shows |
| --- | --- |
| `verify-run-1.txt` | The first full run, including any failures |
| `fix-log.md` | A table of every failure: message, cause, fix, and the re-run |
| `verify-run-final.txt` | The final run ending `N passed, 0 failed, M skipped` |
| `snapshots.png` | Your `lab-verified` snapshots in VMware and Proxmox |
| `evidence.md` | Your filled-in evidence log |

## Explain it in your own words

1. Choose one check and describe, step by step, what it does to test a service.
2. The `20-weak-defaults` check passes when things are *weak*. Why does the course want that?
3. What was your hardest failure, and how did you find the cause?

## If it goes wrong

- Each check's message says what it expected and usually which guide to re-read. Run one check at a time
  with `./verify/verify.sh --only NAME` while you fix things.
- `20-weak-defaults` failing is actually useful information: it means something was hardened before the
  baseline measurement in the security weeks. If you did that on purpose, note it; if not, you may want to
  rebuild that guest.
- A check times out: some services take a minute after a restart. Wait and run it again before changing
  anything.
- You are far behind: ask your lecturer which checks matter most for your assessment. A partly working lab
  with honest evidence is better than a faked clean run.

You now have a complete, working "business in a box". The security loop (measure, harden, re-measure) starts
from here.
