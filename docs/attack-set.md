# The attack set

Five small attacks, run from `admin01` against your own lab only (your scope file is checked first). The
whole set takes about 20 minutes. The same set runs in week 12 (default lab) and week 17 (hardened lab),
so the two reports are comparable. Each finding id is stable: `attack:<id>:<detail>`.

| Id                | Layer    | What it tries                                                         | What a finding means                                              |
| ----------------- | -------- | --------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `enum-services`   | service  | Scan all TCP ports and read service banners (`nmap -sV`)              | A reachable service an attacker can see and fingerprint            |
| `ssh-weak-creds`  | identity | Try a tiny fixed list of common usernames and passwords over SSH      | A login that worked with a guessable password                      |
| `web-basics`      | service  | Read the web server's response headers                                | Missing browser protections, or a server banner that names its version |
| `mail-basics`     | service  | Ask the mail server whether it relays for strangers and answers `VRFY` | An open relay, or a way to confirm which users exist               |
| `anon-directory`  | identity | List shares on the file server without logging in                     | A share an anonymous visitor can see                               |

Read a finding as "an attacker on the LAN could do this", not as a score. Week 17 asks what closed, what
did not, and why.

## Tools

Installed on `admin01` by the week 12 steps: `nmap`, `hydra`, `curl`, `smbclient`. All are open source.
