# 09: Squid

## What you will build

The filtering forward proxy on `pfsense01`.

**Time and difficulty:** 1 to 1.5 hours. Easy. It is all web-page clicking in pfSense, and the result is
visible right away.

## Why

A forward proxy is a different thing from the reverse proxy (Traefik) you will build in guide 10: this one
sits between your LAN clients and the internet, and lets you see and filter what they ask for.

> **What's going on:** Without a proxy, a computer talks to a website directly. With a **forward proxy**,
> the computer asks Squid, and Squid fetches the page on its behalf. That gives the business one place to
> write down who visited what, and to block categories of sites. A **reverse proxy** is the opposite:
> visitors reach it first and it passes them on to the right internal server. Remember the pair: _forward
> protects users going out; reverse fronts servers coming in._

## Steps

Follow [lab/pfsense/squid.md](../../lab/pfsense/squid.md) in full. It is a GUI walkthrough, not a script,
because Squid's settings do not import cleanly across pfSense versions.

> **Evidence:** Take a screenshot of each pfSense settings page as you save it (General, ACLs). They are
> your proof of what you configured, and pfSense's pages are the only record.

> **Careful:** Leave **Transparent proxy** and **SSL/MITM** off. Turning on SSL interception makes Squid
> impersonate every website's certificate, a much bigger job that this lab does not cover.

## Check it worked

```bash
curl -x http://10.10.10.1:3128 -I https://example.com
```

returns `HTTP/1.1 200` (or a redirect). A request to a domain on your blacklist returns `403`. The
`squid.md` file lists the exact second command. Then open **Services > Squid Proxy Server > Real Time** in
pfSense and watch both requests appear.

## Evidence to capture

> **Beginner tip:** `make evidence GUIDE=09` (from `lab/`) runs the read-only commands for you and saves them, stamped with your name, the date and the machine, in `auto-evidence.txt` in your evidence folder. Read it before you commit. It does not replace your screenshots, your notes or your own explanation.

Save in `portfolio/evidence/09-squid/`:

| File                 | What it shows                                                        |
| -------------------- | -------------------------------------------------------------------- |
| `squid-general.png`  | The Squid **General** page: enabled, LAN, port 3128, transparent off |
| `squid-acls.png`     | The **ACLs** page showing the allowed subnet and your blacklist      |
| `curl-allowed.txt`   | The allowed request returning 200 or a redirect, with the prompt     |
| `curl-blocked.txt`   | The blocked request returning 403                                    |
| `squid-realtime.png` | The Real Time log with both requests listed                          |
| `evidence.md`        | Your filled-in evidence log                                          |

## Explain it in your own words

1. What is the difference between a forward proxy and a reverse proxy? Give one example of each from this
   lab.
2. A user can bypass the proxy by changing a browser setting. What does that tell you about proxies as a
   security control?

## If it goes wrong

- See the "Check it worked" steps inside `squid.md` itself; it includes the Real Time log view, which shows
  every request as it happens.
- The `curl` command hangs or times out: Squid is not listening on the LAN interface. Check **Services >
  Squid Proxy Server > General** and that the package is enabled and running (**Status > Services**).
- The blocked domain is not blocked: save and **Apply** on the ACLs page, and use a name exactly as typed.

### Where to look

| What                 | Command or place                                           |
| -------------------- | ---------------------------------------------------------- |
| Live requests        | **Services > Squid Proxy Server > Real Time**              |
| Squid status         | **Status > Services** in pfSense                           |
| Squid's own log      | **Status > System Logs > Packages** (Squid)                |
| From the client side | `curl -v -x http://10.10.10.1:3128 -I https://example.com` |
