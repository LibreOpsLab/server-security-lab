# Squid on pfSense: the filtering forward proxy

Squid is the lab's **forward proxy**: LAN clients send their web traffic through it so you can filter and
log it. (Traefik on `docker01` is the opposite thing, a *reverse* proxy in front of the apps.)

It is set up by hand from these steps, not imported in `config.xml`, because package settings in the
configuration file change between pfSense versions.

Settings agreed for the lab:

| Setting | Value |
| ------- | ----- |
| Package | `squid` from the pfSense **CE** package manager |
| Mode | Explicit forward proxy, listening on **port 3128**, LAN interface only |
| TLS | no SSL interception (no SSL bump): HTTPS passes through as a tunnel, so the lab CA is not involved |
| Logging | Access log on, so you can see requests in the log week |

## Steps

1. **System > Package Manager > Available Packages**, search for `squid`, **Install**.
2. **Services > Squid Proxy Server > Local Cache**: keep the defaults (a small disk cache is fine).
3. **Services > Squid Proxy Server > General**:
   - Enable Squid Proxy.
   - Proxy Interface(s): **LAN**.
   - Proxy Port: **3128**.
   - Transparent HTTP Proxy: **off**. SSL/MITM mode: **off** (no SSL interception).
   - Allow Users on Interface: **on**.
   - Save.
4. **Services > Squid Proxy Server > ACLs**:
   - Allowed Subnets: `10.10.10.0/24`.
   - Blacklist: add a few example domains, one per line (for example `example-blocked.test`).
   - Save, then **Apply**.
5. **Services > Squid Proxy Server > Real Time** to watch requests as they arrive.

## Check it worked

From `admin01`:

```bash
curl -x http://10.10.10.1:3128 -I https://example.com        # works: HTTP/1.1 200 or a redirect
curl -x http://10.10.10.1:3128 -I http://example-blocked.test  # refused by Squid (403)
```

Then look at **Real Time** in pfSense: both requests are listed.

## Why it matters later

A filtering proxy is one layer of defence in depth. In the security weeks you will see what it does and
does not stop, and that a client which ignores the proxy settings simply bypasses it.
