# 07: Identity

## What you will build

`samba-dc01`: Samba Active Directory. This is the lab's single source of identity. Every other service in
the lab checks a username and password against this one.

**Time and difficulty:** 2 to 3 hours. Medium. The command is short; the concepts (directories, domains,
LDAP, Kerberos) are the hardest ideas in the build, so read the explanations.

## Why

Real small businesses run on one directory, not a different login for every app. Building that first, and
building everything else to use it, is the point of the "business in a box" design.

> **What's going on:** A **directory** is a central list of people (users), groups they belong to, and
> computers. **Active Directory** is Microsoft's version; **Samba** is the open-source version of it. A
> **domain controller (DC)** is the server that holds the directory and answers "is this password right?".
> Applications talk to it using **LDAP** (to ask who someone is and which groups they are in) and
> **Kerberos** (to prove who someone is with tickets). The DC also runs DNS for `lab.internal`, which is why
> AD and DNS are bound together: clients find the DC by name.

## Before you start

- Guide 06 is complete and `samba-dc01` (`10.10.10.21`) answers a ping.
- Take a snapshot of `pve01` and `admin01` called `before-make-identity`. Samba provisioning cannot be
  re-run cleanly (see "If it goes wrong").
- Open `lab/data/users.csv` and read it. This is the list of staff your lab will create.

## Steps

1. Read first. Open `lab/ansible/roles/samba_dc/tasks/main.yml` and `lab/data/users.csv`. In your
   evidence, note the names of three staff and the groups they are in, and one thing about the role you do
   not understand yet.
2. Build the identity layer:

   ```bash
   cd lab
   make trust       # every guest trusts the lab certificate authority
   make identity    # builds samba-dc01, DNS records, and the lab's users and groups
   ```

   This provisions the domain `lab.internal`, installs the DC's certificate, and creates the users and
   groups in `lab/data/users.csv`.

   > **What's going on:** `make trust` copies the lab's root certificate to every guest and tells it to
   > trust certificates signed by it. `make identity` then installs Samba, creates the domain, issues the
   > DC a certificate (so LDAP can be encrypted, "LDAPS") and loads the users from the CSV file.

   > **Careful:** **The domain's password policy starts deliberately relaxed** (short passwords allowed, no
   > lockout). This is the lab's default state; the security weeks later measure it and then tighten it.
   > Do not harden it now, and do not "improve" `users.csv`.

3. Test that the directory answers. On `admin01`:

   ```bash
   ldapsearch -x -H ldaps://samba-dc01.lab.internal -s base -b "" namingContexts
   ```

   > **What's going on:** This asks the directory a harmless question ("what do you hold?") over an
   > encrypted connection. If the answer comes back, three things are true at once: DNS found the DC, the
   > DC is listening, and `admin01` trusts its certificate.

   > **Beginner tip:** Read the output. A line such as `namingContexts: DC=lab,DC=internal` is the success
   > message. If you only see an error, copy it into your evidence and read "If it goes wrong".

## Check it worked

- The `ldapsearch` command above returns results, not an error.
- On `samba-dc01`: `samba-tool user list` includes the staff from `users.csv`. Run it with:
  `ssh -i ~/.ssh/lab_admin root@10.10.10.21 samba-tool user list`.
- `ssh -i ~/.ssh/lab_admin root@10.10.10.21 samba-tool domain level show` prints the domain's functional
  level, showing the domain exists.

## Evidence to capture

Save in `portfolio/evidence/07-identity/`:

| File                | What it shows                                                                  |
| ------------------- | ------------------------------------------------------------------------------ |
| `reading-notes.md`  | The three staff and groups you noted, and the one thing you did not understand |
| `make-trust.txt`    | Output of `make trust` ending with the recap                                   |
| `make-identity.txt` | Output of `make identity` ending with the recap                                |
| `ldapsearch.txt`    | The `ldapsearch` command and its successful output                             |
| `user-list.txt`     | `samba-tool user list` output (usernames only, never passwords)                |
| `evidence.md`       | Your filled-in evidence log                                                    |

## Explain it in your own words

1. What is a domain controller, and what do the other servers in the lab ask it?
2. Why does DNS for `lab.internal` live on the domain controller?
3. The password policy is deliberately weak. Give one reason a business might leave it that way, and one
   reason an attacker would love it.

## If it goes wrong

- `samba-tool domain provision` refuses to run again: this is expected; Samba AD provisioning is not
  re-runnable. To start over, wipe `/var/lib/samba` on `samba-dc01` and re-run `make identity`
  (destructive), or restore the snapshot you took before this guide.
- LDAPS fails with a certificate error: run `make trust` again and confirm it ran for `admin01` too.
- `ldapsearch: command not found`: `sudo apt install -y ldap-utils` on `admin01`.
- Name not found for `samba-dc01.lab.internal`: `admin01` is not asking the lab's DNS. Check the lab
  adapter's DNS is set to `10.10.10.1` (guide 02, step 7) and that pfSense forwards `lab.internal` to the
  DC (guide 08).
- The play fails on the Samba package or the container's permissions: copy the first error and ask your
  lecturer. The DC runs in a _privileged_ container on purpose (see the design document); this is a known
  risk area for the first real build.
