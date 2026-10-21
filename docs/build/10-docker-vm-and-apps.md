# 10: Docker VM and apps

## What you will build

`docker01`: Traefik, NextCloud, Stirling PDF and Vaultwarden.

## Why

A small business needs shared files, document tools and a password manager. Running them as containers
behind one reverse proxy is how most small teams actually deploy this kind of thing today.

## Steps

```bash
cd lab
make services   # builds auth01 (needed for sign-in) and issues the app certificates
make apps       # deploys docker01
```

NextCloud's first run can take a few minutes; the role waits for it.

## Check it worked

- `https://cloud.lab.internal`, `https://pdf.lab.internal` and `https://vault.lab.internal` all load with a
  valid certificate (the lab CA, once trusted by your browser or OS — see guide 05).
- `make verify` later checks all three automatically.

## If it goes wrong

- A container will not start: `ssh root@10.10.10.30`, then `cd /opt/lab/<stack> && docker compose logs`.
- Certificate errors in the browser: your machine does not trust the lab root CA yet; import
  `lab/secrets/ca/root/certs/ca.cert.pem` into its trust store.
