# Week 17: attack it again, then compare

Same tools, same scripts, same hosts as week 12. The only thing that changed is what you built in week 15.

**Your lab only**, as before.

## Steps

1. Make sure your week 12 `default` reports and week 15 `hardened` audits are committed.
2. Run the check for each host. It re-runs the audit and the attack set, then compares each tool:

   ```bash
   weeks/17-reattack-compare/check.sh docker01 samba-dc01
   ```

3. Read the comparison reports in `portfolio/reports/` (`compare-*.md`). They list the gaps first:
   _unchanged_ (still open), _new_ (something your hardening introduced) and _reduced_, then _closed_.
   _Not compared_ means a tool did not run this time; fix that and run again.
4. Pick each finding that is still open and decide: remediate it, or accept it and say why.
5. Remediate what you chose, then run the check again so the comparison shows it.
6. Finish `portfolio/reflection.md`.

5a. **Brief the manager again.** Run `PYTHONPATH=scaffold python3 -m sslab impact --before <week 12 report> --after <this week's report>` and fill it in, copy the briefing template to `portfolio/manager-briefing-2.md`, and have the second conversation: what changed, what's still open, and why.

> **What's going on:** The comparison matches each finding in your `default` run with the same finding in
> the new run by its id, so the difference is down to what you changed. Read the **gaps first**:
> _unchanged_ and _new_ are where the learning is. A finding you left open on purpose, with a good reason, is
> a better answer than one you closed by accident.

> **Beginner tip:** If a tool shows _not compared_, it did not run this time (a typo, a host that was
> down, a missing tool). Fix that and run again. Do not hand in a comparison with _not compared_ rows you
> have not explained.

## Evidence to capture

| Where | What it shows |
| --- | --- |
| `portfolio/reports/compare-*.md` | The comparison reports, unedited |
| `portfolio/remediation-record.md` | For each finding still open: remediate or accept, and your reason |
| `portfolio/manager-briefing-2.md` | The second plain-language briefing note |
| `portfolio/reflection.md` (finished) | The completed reflection, including one control that cost something |
| `portfolio/evidence/17-reattack/evidence.md` | Problems you hit and how you fixed them |

## Explain it in your own words

1. Which finding is still _unchanged_, and why did you leave it?
2. Did your hardening introduce anything _new_? What does that tell you about the cost of security?

## What you hand in

The `hardened` reports, the comparison reports, your remediation record and your finished reflection. You
are marked on what changed and what you understood about it, not on the score.
