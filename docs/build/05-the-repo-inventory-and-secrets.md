# 05: The repo, inventory and secrets

## What you will build

Your own private copy of the lab repo, and the generated secrets and certificate authority every later guide
depends on.

**Time and difficulty:** 1 to 2 hours. Mostly reading and understanding, then two commands. This is the
guide to take your time over: it introduces the idea the rest of the lab runs on.

## Why

A GitHub fork of a public repository is always public, and your copy will contain your lab's details. A
private copy with the full history behaves like a fork for day-to-day work (`git fetch upstream`,
`git merge upstream/main`) without being visible to anyone else. See
[docs/git-workflow.md](../git-workflow.md).

> **What's going on:** There are two big ideas here. **One source of truth:** every hostname, address and
> RAM size lives in a single file, and every script, template and document reads it. Change it once and the
> whole lab follows. **Secrets stay out of Git:** passwords and the certificate authority's private keys are
> generated on your machine, kept in a folder Git ignores, and backed up somewhere safe. If they ended up in
> your repository they would be exposed to anyone who ever sees it.

## Steps

1. **Your repository.** In class, your lecturer gives you the URL of a private repository, and you cloned
   it on `admin01` in guide 04. Check it is the right one:

   ```bash
   cd ~/server-security-lab
   git remote -v
   ```

   `origin` should be _your_ private repository. If you are studying alone or have no private repo, make
   one with the script below (this needs `gh` logged in, as in guide 04). Skip this if you already have a
   private repo:

   ```bash
   bash <(curl -fsSL https://raw.githubusercontent.com/LibreOpsLab/server-security-lab/main/scripts/create-private-copy.sh) server-security-lab
   cd server-security-lab
   ```

   > **Careful:** Piping a script from the internet into `bash` runs whatever is at that address with your
   > permissions. It is acceptable here because your lecturer points you at this exact repository. Make a
   > habit of opening a script and reading it first: `curl -fsSL <url> | less`.

2. **Read the single source of truth.** Open `lab/inventory/group_vars/all.yml` in VS Code or a text
   editor. Find: the domain name, the network range, and the `lab_hosts` list. Every hostname, address and
   RAM figure the rest of the build uses comes from this one file.

   > **Beginner tip:** The file is YAML: indentation matters, and `key: value` pairs describe things. You
   > will meet YAML again in every Ansible file. A tab character where spaces are expected breaks it.

3. **Generate the secrets and the certificate authority** (never prints a value):

   ```bash
   scripts/gen-secrets.sh
   ```

   > **What's going on:** This creates a random password for each service, plus a two-level certificate
   > authority (CA): a _root_ CA that stays offline, and an _intermediate_ CA that signs the certificates
   > for your servers. Later, every machine is told to trust the root, so every server certificate it signs
   > will show a padlock, not a warning. It is a miniature version of how the real web's HTTPS works.

4. **Back up `lab/secrets/` somewhere outside the repo** (it is gitignored on purpose), because a wiped PC
   loses it otherwise. Plug in your USB drive, find where it is mounted (for example under `/media/`), then:

   ```bash
   scripts/backup-secrets.sh /path/on/your/usb/secrets.age
   ```

   You will be asked for a passphrase to encrypt the backup.

   > **Careful:** If you forget the passphrase, the backup is useless. Store it in a password manager or
   > somewhere only you can reach. Never commit it. Never put the USB drive in a shared PC drawer.

## Check it worked

- `lab/secrets/` contains one file per secret, plus a `ca/` directory with `root/` and `intermediate/`.
  Check with `ls lab/secrets` (look at the _names_; do not print file contents).
- `openssl verify -CAfile lab/secrets/ca/root/certs/ca.cert.pem lab/secrets/ca/intermediate/certs/intermediate.cert.pem`
  says `OK`.
- `git status` does not list anything inside `lab/secrets/`. Git is ignoring it as intended.
- The backup file exists on the USB drive and is not empty (`ls -l`).

## Evidence to capture

> **Beginner tip:** `make evidence GUIDE=05` (from `lab/`) runs the read-only commands for you and saves them, stamped with your name, the date and the machine, in `auto-evidence.txt` in your evidence folder. Read it before you commit. It does not replace your screenshots, your notes or your own explanation.

Save in `portfolio/evidence/05-the-repo-inventory-and-secrets/`:

| File                     | What it shows                                                                                         |
| ------------------------ | ----------------------------------------------------------------------------------------------------- |
| `git-remote.txt`         | `git remote -v`, showing your own private repository                                                  |
| `inventory-excerpt.txt`  | The first 30 lines of `all.yml` (`head -30 lab/inventory/group_vars/all.yml`); it contains no secrets |
| `secret-names.txt`       | `ls lab/secrets` (file _names_ only, no contents)                                                     |
| `openssl-verify.txt`     | The `openssl verify` command and its `OK` output                                                      |
| `git-status-ignored.txt` | `git status` showing `lab/secrets/` is not listed                                                     |
| `backup-listing.txt`     | `ls -l` of the backup file on the USB drive (not its contents)                                        |
| `evidence.md`            | Your filled-in evidence log                                                                           |

> **Careful:** The evidence for this guide is about _secrets_. Double-check each file before committing: no
> passwords, no `.pem` key contents, no passphrase.

## Explain it in your own words

1. Why is `lab/secrets/` kept out of Git, and what would go wrong if it were committed?
2. What does the "single source of truth" mean here? Give one example of a place the inventory is used.
3. Why do we make a _private copy_ rather than a fork?

## If it goes wrong

- Running `gen-secrets.sh` again: it is safe. Existing secrets and the CA are never overwritten.
- Lost the USB backup: you cannot recover the CA's private keys; delete `lab/secrets/` and run
  `gen-secrets.sh` again, which issues a fresh CA, and re-run `make trust` on every guest afterwards.
- `gh: command not found` or `gh auth` errors: install `gh` (`sudo apt install gh`) and run
  `gh auth login` again.
- `Permission denied` running a script: run it as `bash scripts/gen-secrets.sh`, or ask your lecturer why
  the executable bit is missing.
- `openssl verify` says `unable to get local issuer certificate`: the paths are wrong, or the secrets are
  half-generated. Delete `lab/secrets/` and run `gen-secrets.sh` again.

### Where to look

| What                          | Command or place                                                                                                       |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| What Git sees                 | `git status` and `git remote -v`                                                                                       |
| What the secrets folder holds | `ls lab/secrets` (names only)                                                                                          |
| The CA chain                  | `openssl verify -CAfile lab/secrets/ca/root/certs/ca.cert.pem lab/secrets/ca/intermediate/certs/intermediate.cert.pem` |
| Script errors                 | `bash -x scripts/gen-secrets.sh 2>&1                                                                                   | head -50` (shows commands, not secret values) |
