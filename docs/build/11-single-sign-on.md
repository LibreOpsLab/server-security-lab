# 11: Single sign-on

## What you will build

`auth01`: Authelia, the lab's sign-in portal. NextCloud uses it as an OpenID Connect provider; Stirling PDF
and the Vaultwarden web vault sit behind it as a forward-auth gate.

**Time and difficulty:** 1.5 to 2.5 hours. Medium. The build is one command; understanding the sign-in flow
and trying the second factor is the real work.

> **Do this before guide 10.** The apps in guide 10 need the sign-in portal to exist. The week map puts
> this guide first for that reason, even though it is numbered 11.

## Why

A real small business does not want a different login for every application. This is also where you meet
the pattern you will use again and again: a second factor (TOTP) required only for the accounts that matter
most (the `admins` group).

> **What's going on:** With **single sign-on (SSO)** you sign in once at a central portal, and every
> application trusts that portal. Authelia checks your username and password against Samba AD (using
> LDAP, from guide 07) so there is still only one list of people. **OIDC** is the standard way an app such
> as NextCloud says "send the user to Authelia, and tell me who they are." Apps that cannot do OIDC sit
> behind **forward auth**: Traefik asks Authelia "is this person signed in?" before it lets a request
> through. **TOTP** is the six-digit code from an authenticator app, which is a second proof of identity.

## Before you start

- Guides 07 and 08 are complete (identity, DNS, time).
- Take a snapshot of `pve01` called `before-make-sso`.
- Install an authenticator app on your phone, or use a desktop one you trust, to try the second factor.

## Steps

1. Read first. Open `lab/ansible/roles/authelia/templates/configuration.yml.j2`. Find where the LDAP server
   is named, and where the `admins` group is required to use a second factor. Note both in your evidence.
2. Build the portal:

   ```bash
   cd lab
   make sso
   ```

   (`make services` also builds it, but along with the file, mail and Wi-Fi servers. The guides build them
   one at a time so you can see which step breaks.)

   > **Beginner tip:** Authelia installs from its official Debian package at a pinned version. If the
   > package download fails, check `authelia_deb_sha256` in
   > `lab/ansible/roles/authelia/defaults/main.yml` is still correct against the current release on GitHub
   > (release checksums occasionally change when a release is re-cut). A checksum is a fingerprint of a file:
   > it proves the download is the one the author intended.

3. Try it. In a browser on `admin01`, open `https://auth.lab.internal`. If the browser warns about the
   certificate, it does not trust the lab's root CA yet; the browser on `admin01` needs
   `lab/secrets/ca/root/certs/ca.cert.pem` imported (Firefox: **Settings > Privacy & Security >
   Certificates > View Certificates > Authorities > Import**). Note that `make trust` handled the _system_
   store, not Firefox's own.
4. Sign in as an ordinary user (for example `alice`, with the starting password from `lab/data/users.csv`),
   then sign in as an `admins` user (for example `erin`) and register a TOTP device.

   > **Careful:** There is no mail relay wired in, so Authelia cannot email you the registration link. It
   > writes one-time links to `/var/lib/authelia/notification.txt` on `auth01`. Read it with:
   > `ssh -i ~/.ssh/lab_admin root@10.10.10.22 cat /var/lib/authelia/notification.txt`. Never post one of
   > these links in a screenshot that anyone else will see.

## Check it worked

- `https://auth.lab.internal` shows the Authelia sign-in page.
- Signing in as a user in the `admins` group asks for a TOTP code; signing in as any other user does not.

## Evidence to capture

Save in `portfolio/evidence/11-single-sign-on/`:

| File                    | What it shows                                                                |
| ----------------------- | ---------------------------------------------------------------------------- |
| `reading-notes.md`      | Where the LDAP server and the second-factor rule live in the config          |
| `make-sso.txt`          | Output of `make sso` ending with the recap                                   |
| `portal.png`            | The sign-in page with the padlock and `auth.lab.internal` in the address bar |
| `normal-login.png`      | An ordinary user signed in, with no second-factor prompt                     |
| `admin-totp-prompt.png` | An `admins` user being asked for a code (do not show the QR code or secret)  |
| `evidence.md`           | Your filled-in evidence log                                                  |

## Explain it in your own words

1. In your own words, follow one sign-in: what does the app, the portal and the directory each do?
2. Why require a second factor only for the `admins` group and not for everyone?
3. Which would you rather defend: ten apps each with their own login, or one portal? Why?

## If it goes wrong

- `authelia validate-config` fails during the Ansible run: the error names the exact line; most issues are a
  missing secret file (re-run `scripts/gen-secrets.sh`).
- The browser warns "Not secure": the browser does not trust the lab CA yet (step 3).
- You can sign in as one user but not another: check the user exists (`samba-tool user list`, guide 07) and
  that the password has not been changed.
- A sign-in loop or "invalid credentials" for everyone: check time is correct on `auth01` and `samba-dc01`
  (`chronyc sources`, guide 08), then check Authelia can reach the DC: `nc -zv 10.10.10.21 636` from
  `auth01`.
