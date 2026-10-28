# 13: File transfer and shares

## What you will build

`files01`: a domain-joined file server with Samba (SMB) shares and chrooted SFTP.

**Time and difficulty:** 1.5 to 2.5 hours. Medium. Joining a domain depends on DNS and time being right, so
this guide quietly tests your earlier work.

## Why

Most small businesses need both: SMB for everyday desktop use, SFTP for scripted or remote transfers.

> **What's going on:** **SMB** is the protocol behind Windows file shares ("map a network drive"). **SFTP**
> is file transfer over SSH, so it is encrypted and can be scripted. A **chroot** locks a user into one
> folder: they see their own directory as the whole world and cannot walk up into anyone else's. The server
> is a **domain member**: it joins `lab.internal` so staff sign in with their directory password and the
> shares can be limited by group (`staff`, `finance`).

## Before you start

- Guides 07 and 08 are complete, and time is in sync.
- Take a snapshot of `pve01` called `before-make-files`.

## Steps

1. Read first. Open `lab/ansible/roles/files_server/templates/smb.conf.j2`. Find the three shares and who
   is allowed to use each. Note them.
2. Build the file server:

   ```bash
   cd lab
   make files
   ```

3. List the shares without signing in:

   ```bash
   smbclient -N -L //files01.lab.internal
   ```

   > **Beginner tip:** `-N` means "no password" and `-L` means "list". If `smbclient` is missing:
   > `sudo apt install -y smbclient`.

4. Try SFTP as a lab user. You are inside a chroot: prove it.

   ```bash
   sftp alice@files01.lab.internal
   sftp> pwd
   sftp> cd ..
   sftp> ls
   ```

   > **Stop and check:** After `cd ..` you should still be inside your own directory. If you can see other
   > staff's folders, the chroot is not working. Record it and ask for help.

## Check it worked

```bash
smbclient -N -L //files01.lab.internal
```

lists `staff`, `finance` and `notices`. Log in over SFTP as a staff user; you should land in your own
directory and be unable to go above it.

## Evidence to capture

> **Beginner tip:** `make evidence GUIDE=13` (from `lab/`) runs the read-only commands for you and saves them, stamped with your name, the date and the machine, in `auto-evidence.txt` in your evidence folder. Read it before you commit. It does not replace your screenshots, your notes or your own explanation.

Save in `portfolio/evidence/13-file-transfer-and-shares/`:

| File                 | What it shows                                                                      |
| -------------------- | ---------------------------------------------------------------------------------- |
| `reading-notes.md`   | The three shares and who may use each                                              |
| `make-files.txt`     | Output of `make files` ending with the recap                                       |
| `smbclient-list.txt` | The share list from `smbclient -N -L`                                              |
| `sftp-session.txt`   | Your SFTP session showing `pwd`, `cd ..` and that you stayed in your own directory |
| `evidence.md`        | Your filled-in evidence log                                                        |

## Explain it in your own words

1. When would a business pick SMB, and when SFTP?
2. What is a chroot, and why is it a useful security control?
3. The `notices` share needs no password. What kind of thing is it appropriate for, and what would be a
   bad thing to put in it?

## If it goes wrong

**Run this first:** `make preflight STAGE=services`. It checks what this guide depends on and says what to fix.

- `net ads join` fails: confirm `make identity` completed and time is in sync (guide 08).
- `smbclient` says `NT_STATUS_...`: the file server is not running Samba yet or the DNS name is wrong. Try
  the address `10.10.10.26` directly.
- SFTP says `Permission denied`: check the username exists and the password is right. The password policy
  is deliberately weak, but passwords are still case-sensitive.
- **Note:** the `notices` share is deliberately open to anyone on the LAN without logging in. That is this
  guide's contribution to the security loop, not a misconfiguration.

### Where to look

| What                        | Command or place                                           |
| --------------------------- | ---------------------------------------------------------- |
| Samba and SSH state         | `ssh root@10.10.10.26 systemctl status smbd ssh`           |
| Samba log                   | `ssh root@10.10.10.26 journalctl -u smbd -n 50 --no-pager` |
| Domain membership           | `ssh root@10.10.10.26 net ads testjoin`                    |
| Share settings Samba loaded | `ssh root@10.10.10.26 testparm -s`                         |
| SFTP debugging              | `sftp -v alice@files01.lab.internal`                       |
