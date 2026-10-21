# 05: The repo, inventory and secrets

## What you will build

Your own private copy of the lab repo, and the generated secrets and certificate authority every later guide
depends on.

## Why

A GitHub fork of a public repository is always public, and your copy will contain your lab's details. A
private copy with the full history behaves like a fork for day-to-day work (`git fetch upstream`,
`git merge upstream/main`) without being visible to anyone else. See
[docs/git-workflow.md](../git-workflow.md).

## Steps

1. On `admin01`:

   ```bash
   bash <(curl -fsSL https://raw.githubusercontent.com/LibreOpsLab/server-security-lab/main/scripts/create-private-copy.sh) server-security-lab
   cd server-security-lab
   ```

2. Look at `lab/inventory/group_vars/all.yml`: every hostname, address and RAM figure the rest of the build
   uses comes from this one file.
3. Generate the secrets and the certificate authority (never prints a value):

   ```bash
   scripts/gen-secrets.sh
   ```

4. **Back up `lab/secrets/` somewhere outside the repo** (it is gitignored on purpose), because a wiped PC
   loses it otherwise:

   ```bash
   scripts/backup-secrets.sh /path/on/your/usb/secrets.age
   ```

## Check it worked

- `lab/secrets/` contains one file per secret, plus a `ca/` directory with `root/` and `intermediate/`.
- `openssl verify -CAfile lab/secrets/ca/root/certs/ca.cert.pem lab/secrets/ca/intermediate/certs/intermediate.cert.pem`
  says `OK`.

## If it goes wrong

- Running `gen-secrets.sh` again: it is safe. Existing secrets and the CA are never overwritten.
- Lost the USB backup: you cannot recover the CA's private keys; delete `lab/secrets/` and run
  `gen-secrets.sh` again, which issues a fresh CA, and re-run `make trust` on every guest afterwards.
