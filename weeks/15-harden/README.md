# Week 15: harden, layer by layer

Close what week 12 found, by writing the controls yourself as code in `build/`. The point is not a
perfect score. It is to know what each control does and what it costs.

## Steps

1. Pick the findings from your week 12 reports that matter most for your design. Say why, in
   `build/hardening-notes.md`.
2. Copy `starter/harden.yml` to `build/harden.yml` and complete every `TODO`. Work across the layers:
   network (pfSense rules), host (SSH, accounts, services, updates), service (web, mail, file shares)
   and identity (passwords, second factor, least privilege).
3. Run it against a **clone** first, then the real guest. Keep the snapshot until you are sure.
4. Measure the hardened lab:

   ```bash
   weeks/15-harden/check.sh docker01 samba-dc01
   ```

   It refuses to run for a host with no week 12 report, because there would be nothing to compare.

5. Copy `portfolio/templates/reflection.md` to `portfolio/reflection.md` and write the first part.

> **What's going on:** Hardening means removing or restricting things so an attacker has less to work with:
> turn off password logins in favour of keys, close ports nothing needs, add the missing web security
> headers, tighten the password policy, require a second factor. Each control has a **cost** (a service that
> breaks, a user who is inconvenienced, maintenance time), and recording that cost is half of the marks.

> **Careful:** Never harden a live guest first. Clone it or restore a snapshot, test the change there, and
> only then apply it. One wrong firewall rule or SSH setting can lock you out of the machine. Keep the
> `pre-security-baseline` snapshot until week 17 is done.

> **Beginner tip:** Change **one control at a time**, then check the service still works (`make verify`
> shows you, apart from `20-weak-defaults`, which is _expected_ to start failing as you harden). Write each
> change into `build/hardening-notes.md` as you make it: what, where, why, and what it cost. Commit after
> every working change so you can undo one.

## Evidence to capture

| Where                                      | What it shows                                                            |
| ------------------------------------------ | ------------------------------------------------------------------------ |
| `build/hardening-notes.md`                 | For every control: what you changed, why you picked it, what it cost     |
| `build/harden.yml` and its run output      | The controls as code, and proof they ran (`ansible-playbook ... \| tee`) |
| A "clone first" record                     | Output or screenshot showing you tested on a clone before the real guest |
| `portfolio/reports/` (`hardened` reports)  | The re-measurement; do not edit                                          |
| `portfolio/evidence/15-harden/evidence.md` | Problems you hit, including anything you broke and how you recovered     |
| `portfolio/reflection.md` (first part)     | Your own words on what you found and what hardening did                  |

## Explain it in your own words

1. Pick the control that gave the biggest improvement for the least effort. Why was it so effective?
2. Pick one control that cost something. What broke or became harder, and would you keep it?

## What you hand in

`build/harden.yml` and its output, the `hardened` reports, your notes on what you chose and why, and the
start of your reflection.
