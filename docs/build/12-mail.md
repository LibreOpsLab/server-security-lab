# 12: Mail

## What you will build

`mail01`: Postfix and Dovecot, with mailboxes and logins checked against Samba AD, plus DKIM signing and
DMARC checking.

## Why

Email is simple to set up and very easy to set up wrong, which is why it gets its own week later in the
course. Building a working, if imperfect, mail server here gives you something real to examine then.

## Steps

```bash
cd lab
make services
```

## Check it worked

- `openssl s_client -connect mail01.lab.internal:993` completes a TLS handshake.
- A test message sent between two lab users (for example with Thunderbird or `swaks`) is delivered.
- `dig TXT lab.internal` shows the SPF record; `dig TXT lab._domainkey.lab.internal` shows the DKIM key.

## If it goes wrong

- Mail "bounces" immediately: check the recipient's `mail` attribute in Samba AD matches
  `user@lab.internal` exactly (the loader in guide 07 sets this).
- **Note:** `VRFY` and relaying for the lab subnet are left at Postfix's defaults on purpose; that is not a
  bug, it is this guide's contribution to the security loop later in the course.
