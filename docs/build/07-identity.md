# 07: Identity

## What you will build

`samba-dc01`: Samba Active Directory. This is the lab's single source of identity. Every other service in
the lab checks a username and password against this one.

## Why

Real small businesses run on one directory, not a different login for every app. Building that first, and
building everything else to use it, is the point of the "business in a box" design.

## Steps

```bash
cd lab
make trust       # every guest trusts the lab certificate authority
make identity     # builds samba-dc01, DNS records, and the lab's users and groups
```

This provisions the domain `lab.internal`, installs the DC's certificate, and creates the users and groups
in `lab/data/users.csv`. **The domain's password policy starts deliberately relaxed** (short passwords
allowed, no lockout): this is the lab's default state, and the security weeks later in the course measure
it and then tighten it. Do not harden it now.

## Check it worked

```bash
ldapsearch -x -H ldaps://samba-dc01.lab.internal -s base -b "" namingContexts
```
should return a result, not an error.

## If it goes wrong

- `samba-tool domain provision` refuses to run again: this is expected; Samba AD provisioning is not
  re-runnable. To start over, wipe `/var/lib/samba` on `samba-dc01` and re-run `make identity` (destructive).
- LDAPS fails with a certificate error: run `make trust` again and confirm it ran for `admin01` too.
