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

## What you hand in

`build/harden.yml` and its output, the `hardened` reports, your notes on what you chose and why, and the
start of your reflection.
