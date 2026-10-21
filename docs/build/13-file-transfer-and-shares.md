# 13: File transfer and shares

## What you will build

`files01`: a domain-joined file server with Samba (SMB) shares and chrooted SFTP.

## Why

Most small businesses need both: SMB for everyday desktop use, SFTP for scripted or remote transfers.

## Steps

```bash
cd lab
make services
```

## Check it worked

```bash
smbclient -N -L //files01.lab.internal
```
lists `staff`, `finance` and `notices`. Log in over SFTP as a staff user; you should land in your own
directory and be unable to go above it.

## If it goes wrong

- `net ads join` fails: confirm `make identity` completed and time is in sync (guide 08).
- **Note:** the `notices` share is deliberately open to anyone on the LAN without logging in. That is this
  guide's contribution to the security loop, not a misconfiguration.
