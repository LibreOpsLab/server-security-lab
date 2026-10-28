# 07: Identity

## What you will build

`samba-dc01`: Samba Active Directory, on a **Debian 13 VM in VMware, outside Proxmox**. This is the lab's single
source of identity. Every other service in the lab checks a username and password against this one.

**Time and difficulty:** 3 to 4 hours, including building the VM by hand. Medium. The command is short; the concepts (directories, domains,
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

> **Why is the domain controller outside Proxmox?** It is the most critical machine in the lab: if it is down,
> nobody can sign in. In a real company you would not host it on the same hypervisor you may need to rebuild
> or restore. A normal VM also gives Samba a real kernel and filesystem, so file permissions, time and
> directory services behave exactly as the Samba documentation describes.

## Before you start

- Guide 06 is complete (the Proxmox guests exist and have the baseline).
- You have the **Debian 13 netinst ISO** from your lecturer.
- Take a snapshot of `admin01` called `before-make-identity`. Samba provisioning cannot be re-run cleanly
  (see "If it goes wrong"). You will snapshot the DC VM too, once it exists.
- Open `lab/data/users.csv` and read it. This is the list of staff your lab will create.

## Steps

1. **Build the VM by hand.** Follow [Reference: build a minimal Debian 13 VM](debian-vm.md) for `samba-dc01`
   (`10.10.10.21`, 1.5 GB RAM, 2 CPUs, 20 GB disk), including the preparation script over SSH. Stop when
   `ssh root@10.10.10.21 hostname` prints `samba-dc01`. Take a VMware snapshot called `dc-os-installed`.
2. **Give it the baseline** and check it is ready:

   ```bash
   cd lab
   make baseline LIMIT=samba-dc01
   make preflight STAGE=identity
   ```

   > **Stop and check:** Every line of the preflight must say `PASS`. A `FAIL` line says what to fix. This
   > saves you from starting a long build that is certain to fail.

3. Read first. Open `lab/ansible/roles/samba_dc/tasks/main.yml` and `lab/data/users.csv`. In your
   evidence, note the names of three staff and the groups they are in, and one thing about the role you do
   not understand yet.
4. Build the identity layer:

   ```bash
   cd lab
   make trust       # every guest trusts the lab certificate authority
   make identity    # builds samba-dc01, DNS records, and the lab's users and groups
   ```

   This provisions the domain `lab.internal`, installs the DC's certificate, and creates the users and
   groups in `lab/data/users.csv`.

   > **What's going on:** `make trust` copies the lab's root certificate to every guest (including the DC) and
   > tells it to trust certificates signed by it. `make identity` then installs Samba, creates the domain, issues the
   > DC a certificate (so LDAP can be encrypted, "LDAPS") and loads the users from the CSV file.

   > **Careful:** **The domain's password policy starts deliberately relaxed** (short passwords allowed, no
   > lockout). This is the lab's default state; the security weeks later measure it and then tighten it.
   > Do not harden it now, and do not "improve" `users.csv`.

5. Test that the directory answers. On `admin01`:

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

> **Beginner tip:** `make evidence GUIDE=07` (from `lab/`) runs the read-only commands for you and saves them, stamped with your name, the date and the machine, in `auto-evidence.txt` in your evidence folder. Read it before you commit. It does not replace your screenshots, your notes or your own explanation.

Save in `portfolio/evidence/07-identity/`:

| File                 | What it shows                                                                  |
| -------------------- | ------------------------------------------------------------------------------ |
| `reading-notes.md`   | The three staff and groups you noted, and the one thing you did not understand |
| `debian-install.png` | The finished Debian 13 install: `cat /etc/os-release` on the DC's console      |
| `prep-script.txt`    | The `ssh ... bash -s` run from the [Debian VM reference](debian-vm.md)         |
| `preflight.txt`      | The `make preflight STAGE=identity` run, all `PASS`                            |
| `make-trust.txt`     | Output of `make trust` ending with the recap                                   |
| `make-identity.txt`  | Output of `make identity` ending with the recap                                |
| `ldapsearch.txt`     | The `ldapsearch` command and its successful output                             |
| `user-list.txt`      | `samba-tool user list` output (usernames only, never passwords)                |
| `evidence.md`        | Your filled-in evidence log                                                    |

## Explain it in your own words

1. What is a domain controller, and what do the other servers in the lab ask it?
2. Why does DNS for `lab.internal` live on the domain controller?
3. The password policy is deliberately weak. Give one reason a business might leave it that way, and one
   reason an attacker would love it.

## If it goes wrong

**Run this first:** `make preflight STAGE=identity`. Once the guide works, run `make evidence GUIDE=07`.

- `samba-tool domain provision` refuses to run again: this is expected; Samba AD provisioning is not
  re-runnable. To start over, wipe `/var/lib/samba` on `samba-dc01` and re-run `make identity`
  (destructive), or restore the snapshot you took before this guide.
- LDAPS fails with a certificate error: run `make trust` again and confirm it ran for `admin01` too.
- `ldapsearch: command not found`: `sudo apt install -y ldap-utils` on `admin01`.
- Name not found for `samba-dc01.lab.internal`: `admin01` is not asking the lab's DNS. Check the lab
  adapter's DNS is set to `10.10.10.1` (guide 02, step 7) and that pfSense forwards `lab.internal` to the
  DC (guide 08).
- The play fails installing Samba packages: the DC cannot reach the internet. On the DC, `ping 1.1.1.1`, then
  `getent hosts deb.debian.org`. Fix the gateway and DNS (both `10.10.10.1`) before the DC provisions itself.
- `samba-tool domain provision` fails: read the last error line. Common causes are a leftover
  `/etc/samba/smb.conf` or a wrong hostname. `hostname -f` on the DC must print `samba-dc01.lab.internal`.

### Where to look

| What                | Command (on `samba-dc01`, as root)                                                      |
| ------------------- | --------------------------------------------------------------------------------------- |
| Is the DC running?  | `systemctl status samba-ad-dc`                                                          |
| Service log         | `journalctl -u samba-ad-dc -n 50 --no-pager`                                            |
| DNS answers locally | `host samba-dc01.lab.internal 127.0.0.1`                                                |
| Kerberos works      | `kinit administrator`, then `klist` (the password is in `lab/secrets/`; never paste it) |
| Domain health       | `samba-tool domain info 127.0.0.1`                                                      |
| Directory content   | `samba-tool user list`, `samba-tool group list`                                         |
| Time                | `chronyc tracking`                                                                      |
