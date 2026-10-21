# 11: Single sign-on

## What you will build

`auth01`: Authelia, the lab's sign-in portal. NextCloud uses it as an OpenID Connect provider; Stirling PDF
and the Vaultwarden web vault sit behind it as a forward-auth gate.

## Why

A real small business does not want a different login for every application. This is also where you meet
the pattern you will use again and again: a second factor (TOTP) required only for the accounts that matter
most (the `admins` group).

## Steps

```bash
cd lab
make services
```

Authelia installs from its official Debian package at a pinned version. If the package download fails,
check `authelia_deb_sha256` in `lab/ansible/roles/authelia/defaults/main.yml` is still correct against the
current release on GitHub (release checksums occasionally change when a release is re-cut).

## Check it worked

- `https://auth.lab.internal` shows the Authelia sign-in page.
- Signing in as a user in the `admins` group asks for a TOTP code; signing in as any other user does not.
- One-time links (such as a TOTP registration link) are written to
  `/var/lib/authelia/notification.txt` on `auth01` — there is no mail relay wired in, so read it there.

## If it goes wrong

- `authelia validate-config` fails during the Ansible run: the error names the exact line; most issues are a
  missing secret file (re-run `scripts/gen-secrets.sh`).
