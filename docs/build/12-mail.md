# 12: Mail

## What you will build

`mail01`: Postfix and Dovecot, with mailboxes and logins checked against Samba AD, plus DKIM signing and
DMARC checking.

**Time and difficulty:** 2 to 3 hours. Medium to hard. Email has a lot of moving parts. Expect to read logs.

## Why

Email is simple to set up and very easy to set up wrong, which is why it gets its own week later in the
course. Building a working, if imperfect, mail server here gives you something real to examine then.

> **What's going on:** Mail needs several pieces. **Postfix** *sends and receives* mail between servers
> (SMTP). **Dovecot** lets people *read* their mailbox from a client (IMAP). Both ask the directory (Samba
> AD) who the users are. **SPF**, **DKIM** and **DMARC** are three DNS-based checks that help other servers
> decide whether an email really came from your domain: SPF lists which servers may send, DKIM signs each
> message, and DMARC says what to do when the checks fail. Real small businesses get blamed for spam they
> never sent when these are wrong.

## Before you start

- Guides 07 and 08 are complete.
- Take a snapshot of `pve01` called `before-make-mail`.

## Steps

1. Read first. Open `lab/ansible/roles/mail/templates/main.cf.j2` (Postfix's main configuration). Find the
   lines that mention `mynetworks` and `smtpd_...restrictions`. Note what you think each does. (Do not
   change them: some defaults are deliberately left open for the security weeks.)
2. Build the mail server:

   ```bash
   cd lab
   make mail
   ```

3. Send a test message between two lab users. Easiest from `admin01`:

   ```bash
   sudo apt install -y swaks
   swaks --server mail01.lab.internal --from alice@lab.internal --to bob@lab.internal
   ```

   > **Beginner tip:** `swaks` is a "Swiss army knife" for SMTP. It prints the whole conversation between
   > your computer and the server, line by line (lines starting with an arrow pointing right are you, lines pointing left are the server). Reading it is the best
   > way to learn what SMTP is. A line that begins `250` means success.

4. Look at the DNS records that help other servers trust the mail:

   ```bash
   dig TXT lab.internal +short
   dig TXT lab._domainkey.lab.internal +short
   ```

## Check it worked

- `openssl s_client -connect mail01.lab.internal:993 </dev/null` completes a TLS handshake.
- The `swaks` run ends with a `250` response and nothing bounces.
- `dig TXT lab.internal` shows the SPF record; `dig TXT lab._domainkey.lab.internal` shows the DKIM key.

## Evidence to capture

Save in `portfolio/evidence/12-mail/`:

| File | What it shows |
| --- | --- |
| `reading-notes.md` | What you think `mynetworks` and the restrictions do |
| `make-mail.txt` | Output of `make mail` ending with the recap |
| `swaks.txt` | The full `swaks` conversation ending in success |
| `tls-handshake.txt` | The `openssl s_client` output (the first 30 lines are enough) |
| `dns-txt.txt` | Both `dig TXT` results |
| `evidence.md` | Your filled-in evidence log |

## Explain it in your own words

1. Which job does Postfix do, and which does Dovecot do?
2. What problem do SPF, DKIM and DMARC each try to solve? One sentence each.
3. Postfix here allows relaying for the whole lab subnet. Why would that be dangerous on the internet?

## If it goes wrong

- Mail "bounces" immediately: check the recipient's `mail` attribute in Samba AD matches
  `user@lab.internal` exactly (the loader in guide 07 sets this).
- `swaks` cannot connect: check `ping mail01.lab.internal` and that `make mail` finished without a failed
  task.
- Nothing in the mailbox: look at the log on `mail01`: `ssh -i ~/.ssh/lab_admin root@10.10.10.25 tail -50
  /var/log/mail.log`. The line after a failed delivery says why.
- **Note:** `VRFY` and relaying for the lab subnet are left at Postfix's defaults on purpose; that is not a
  bug, it is this guide's contribution to the security loop later in the course.
