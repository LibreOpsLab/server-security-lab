# 08: DNS, DHCP and time

## What you will build

Nothing new to build here: this guide is where you see the pieces from guides 02 and 07 working together.

## Why

DNS, DHCP and time sound separate but depend on each other: Kerberos (used by Samba AD) fails if clocks
drift by more than a few minutes, and DHCP has to hand out the right DNS server or nothing can find
anything by name.

## Steps

There is nothing to run; this is a checkpoint. Read [docs/how-it-works.md] (link in the main README) if you
want the full picture, and confirm the checks below before moving on.

## Check it worked

- A machine that gets its address by DHCP from `pfsense01` also receives `10.10.10.21` (then `10.10.10.1`)
  as its DNS servers.
- `dig samba-dc01.lab.internal @10.10.10.1` (pfSense) returns the same answer as asking `samba-dc01`
  directly: pfSense forwards the lab domain to Samba.
- `chronyc sources` on any guest other than the DC shows `samba-dc01` as its time source.

## If it goes wrong

- Time drifted (Kerberos errors, "clock skew too great"): `chronyc makestep` on the affected guest, or
  re-run `make baseline`.
