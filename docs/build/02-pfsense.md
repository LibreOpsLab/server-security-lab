# 02: pfSense

## What you will build

`pfsense01`: the lab's firewall, DHCP server and DNS forwarder, and later the Squid filtering proxy.

## Why

Every other guest sits behind this one. It is the only guest Ansible does not manage, because its
configuration is its own XML format, not a set of text files.

## Steps

1. Create a new VM: 1 CPU, 1.5 GB RAM, 16 GB disk, two network adapters — one on VMware NAT (internet), one
   on `LAN-LAB`.
2. Install pfSense from the official ISO. At the console "Assign Interfaces" step, note which interface name
   (`em0`, `em1`, ...) pfSense gave each adapter.
3. On your admin machine (once built) or any machine with Python and the repo cloned:

   ```bash
   cd lab/pfsense
   python3 render.py --wan em0 --lan em1 --hostname pfsense01 --out /tmp/config.xml
   ```

4. In pfSense: **Diagnostics > Backup & Restore > Restore configuration**, upload `/tmp/config.xml`.
5. From the console menu, option **3** ("Reset webConfigurator password"), and set a password you will
   remember (it is not in the template).
6. See [09-squid.md](09-squid.md) later for the filtering proxy (not needed yet).

## Check it worked

- The LAN interface answers `https://10.10.10.1` from a machine on `LAN-LAB`.
- `interfaces/lan/ipaddr` in the imported config is `10.10.10.1`.

## If it goes wrong

- Wrong interface names after import: redo the render with the correct `--wan`/`--lan` values and re-import.
- No internet on the LAN yet: that is expected until `admin01` exists in the next few guides.

See `lab/pfsense/README.md` for more detail on the template.
