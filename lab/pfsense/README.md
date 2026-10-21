# pfSense

The lab's firewall, DHCP server, DNS forwarder and Squid proxy. pfSense is configured through its own
interfaces, so it is the one guest Ansible does not manage.

- `config.xml.j2` is the baseline, filled in from the inventory by `render.py`:
  `python3 render.py --wan em0 --lan em1 --out /tmp/config.xml`, then import it with
  **Diagnostics > Backup & Restore**. Interface names are shown at the console "Assign Interfaces" step.
- `squid.md` sets up the proxy by hand.
- The template deliberately keeps pfSense's default "allow LAN to any" rule. See the comment inside it.

Full walkthrough: `docs/build/02-pfsense.md` and `docs/build/09-squid.md`.
