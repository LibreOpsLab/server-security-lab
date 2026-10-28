# 08: DNS, DHCP and time

## What you will build

Nothing new to build here: this guide is where you see the pieces from guides 02 and 07 working together.
It is a checkpoint, and the evidence is a set of tests you run yourself.

**Time and difficulty:** 1 to 2 hours. Easy to run, but this is where networking ideas click, so write your
explanations carefully.

## Why

DNS, DHCP and time sound separate but depend on each other: Kerberos (used by Samba AD) fails if clocks
drift by more than a few minutes, and DHCP has to hand out the right DNS server or nothing can find
anything by name.

> **What's going on:** Three small services quietly hold a network together.
> **DNS** turns names into addresses. **DHCP** gives new machines an address and tells them which DNS server
> and gateway to use. **Time** (NTP) keeps every clock close; Kerberos tickets carry timestamps and are
> rejected if the clocks disagree by more than about five minutes. In this lab pfSense runs DHCP and forwards
> `lab.internal` questions to the DC; the DC keeps its time from pfSense and the other machines follow the
> DC.

## Steps

There is nothing to deploy; this is a checkpoint. Read [How it works](../how-it-works.md) if you want the
full picture, then run each test below on `admin01` and record the result.

1. **DNS from pfSense.** Ask pfSense and the DC the same question and compare:

   ```bash
   dig +short samba-dc01.lab.internal @10.10.10.1
   dig +short samba-dc01.lab.internal @10.10.10.21
   ```

   > **Beginner tip:** `dig` is a DNS question tool. `+short` prints only the answer. `@10.10.10.1` says
   > which server to ask. If `dig` is missing: `sudo apt install -y dnsutils`.

2. **DHCP.** Create a throwaway test VM (any small Linux live ISO) on `LAN-LAB`, or use `win-client01` if you
   built it, set to get its address automatically. It should receive an address in `10.10.10.100` to `.199`
   and `10.10.10.21` then `10.10.10.1` as DNS. If you cannot create a test VM this week, do the other two
   tests and note it in your evidence.
3. **Time.** On any guest other than the DC:

   ```bash
   ssh -i ~/.ssh/lab_admin root@10.10.10.25 chronyc sources
   ```

   You should see `samba-dc01` (or `10.10.10.21`) as the source.

## Check it worked

- A machine that gets its address by DHCP from `pfsense01` also receives `10.10.10.21` (then `10.10.10.1`)
  as its DNS servers.
- `dig samba-dc01.lab.internal @10.10.10.1` (pfSense) returns the same answer as asking `samba-dc01`
  directly: pfSense forwards the lab domain to Samba.
- `chronyc sources` on any guest other than the DC shows `samba-dc01` as its time source.

> **Stop and check:** If time is wrong, fix it now. Single sign-on and Kerberos failures in later guides are
> often just clock drift.

## Evidence to capture

Save in `portfolio/evidence/08-dns-dhcp-and-time/`:

| File                                 | What it shows                                                             |
| ------------------------------------ | ------------------------------------------------------------------------- |
| `dig-compare.txt`                    | Both `dig` commands and their (matching) answers                          |
| `dhcp-lease.png` or `dhcp-lease.txt` | A DHCP client's address and DNS servers (or a note on why you skipped it) |
| `chronyc-sources.txt`                | `chronyc sources` from a non-DC guest, showing the DC as source           |
| `evidence.md`                        | Your filled-in evidence log                                               |

## Explain it in your own words

1. Trace what happens, step by step, when `admin01` looks up `samba-dc01.lab.internal`. Which servers are
   involved?
2. Why would Kerberos fail if one guest's clock was ten minutes wrong?
3. Why do the servers use fixed addresses instead of DHCP?

## If it goes wrong

- Time drifted (Kerberos errors, "clock skew too great"): `chronyc makestep` on the affected guest, or
  re-run `make baseline`.
- `dig` returns nothing from pfSense but works against the DC: pfSense is not forwarding `lab.internal`.
  Check the DNS forwarder settings in pfSense (**Services > DNS Resolver**) and re-import the rendered
  config if needed (guide 02).
- `chronyc sources` shows `samba-dc01` with `?` or no replies: the DC's chrony may not be serving time yet.
  Re-run `make baseline` and wait a minute.
