# 09: Squid

## What you will build

The filtering forward proxy on `pfsense01`.

## Why

A forward proxy is a different thing from the reverse proxy (Traefik) you will build in guide 10: this one
sits between your LAN clients and the internet, and lets you see and filter what they ask for.

## Steps

Follow [lab/pfsense/squid.md](../../lab/pfsense/squid.md) in full. It is a GUI walkthrough, not a script,
because Squid's settings do not import cleanly across pfSense versions.

## Check it worked

```bash
curl -x http://10.10.10.1:3128 -I https://example.com
```
returns `HTTP/1.1 200` (or a redirect). A request to a domain on your blacklist returns `403`.

## If it goes wrong

- See the "Check it worked" steps inside `squid.md` itself; it includes the Real Time log view, which shows
  every request as it happens.
