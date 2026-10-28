# 02: pfSense

## What you will build

`pfsense01`: the lab's firewall, DHCP server and DNS forwarder, and later the Squid filtering proxy.

**Time and difficulty:** 2 to 3 hours. This is your first real network device. The installer is simple;
the new skill is working out which network adapter is which.

> **Do this first:** you need a computer on the private `LAN-LAB` network to open pfSense's web page, and
> your Windows PC is not on it. Do **Part A of [04-admin01.md](04-admin01.md)** now (build `admin01` up to
> and including cloning the repo), then come back here.

## Why

Every other guest sits behind this one. It is the only guest Ansible does not manage, because its
configuration is its own XML format, not a set of text files.

> **What's going on:** A firewall sits between your lab network and the internet. It does four jobs here:
> it *routes* and *NATs* lab traffic out to the internet, it *hands out addresses* (DHCP), it *answers name
> lookups* (DNS) for lab machines, and later it filters web traffic with a proxy (Squid). If the firewall is
> wrong, nothing else in the lab will behave, which is why it comes early.

## Steps

1. Create a new VM: 1 CPU, 1.5 GB RAM, 16 GB disk, two network adapters: **adapter 1 on VMware NAT**
   (internet side) and **adapter 2 on `LAN-LAB`** (lab side). Attach the pfSense ISO.

   > **Beginner tip:** Write down which adapter you made first. pfSense will call them `em0`, `em1` (or
   > `vmx0`, `vmx1`) in the order it finds them, and you must tell it which is which in step 3. Usually the
   > first adapter you added is `em0`.

2. Install pfSense from the official ISO. Accept the defaults. At the console **Assign Interfaces** step,
   note which interface name (`em0`, `em1`, ...) pfSense gave each adapter. Set **WAN** to the NAT adapter
   and **LAN** to the `LAN-LAB` adapter.

   > **What's going on:** WAN means the "wide" side (the internet). LAN means the local side (your lab).
   > Getting them the wrong way round is the most common mistake in this guide, and the symptoms are
   > confusing: you can reach the web page from the wrong side, but nothing has internet.

   > **Evidence:** Photograph the console menu (screenshot the VM) after install showing the WAN and LAN
   > assignments and addresses.

3. On `admin01` (the machine you built in Part A of guide 04), in the repo folder, create the pfSense
   configuration file from the template:

   ```bash
   cd lab/pfsense
   python3 render.py --wan em0 --lan em1 --hostname pfsense01 --out ~/config.xml
   ```

   Use the interface names you noted in step 2. If your WAN is `em0` and your LAN is `em1`, the command
   above is right as written.

   > **What's going on:** `render.py` reads the one inventory file (`lab/inventory/group_vars/all.yml`) and
   > fills in a pfSense configuration template: the lab addresses, DHCP range, DNS forwarding and NAT. Open
   > `lab/pfsense/config.xml.j2` and find the line that gives the LAN address `10.10.10.1`. This is why
   > the guides say "the repo is the lab".

4. Open a browser on `admin01` and go to `https://10.10.10.1`. Your browser will warn about the certificate;
   that is expected (pfSense made one for itself). Accept the warning for now and sign in with the default
   username and password shown in pfSense's own documentation.

   > **Careful:** pfSense ships with a well-known default password. On a real network you would change it
   > immediately. You will do that in step 6, so do not leave this step half done.

   > **Beginner tip:** If `https://10.10.10.1` does not load, check `admin01`'s lab adapter has
   > `10.10.10.10/24` (`ip -br a`) and that both VMs use the same `LAN-LAB` segment. pfSense's default LAN
   > address before the import may be `192.168.1.1` instead; if so, temporarily give `admin01` a
   > `192.168.1.x` address to reach it, then switch back after the import.

5. In pfSense: **Diagnostics > Backup & Restore > Restore configuration**, upload `~/config.xml`, and let it
   reboot.
6. From the pfSense VM console menu, choose option **3** ("Reset webConfigurator password"), and set a
   password you will remember. It is not in the template.

   > **Careful:** Keep this password somewhere safe, but not in the repo. Add it to your notes outside Git.

7. If you changed `admin01`'s lab address to reach the old pfSense page (see the tip in step 4), switch it
   back to `10.10.10.10/24` now. Leave the **gateway blank** as in guide 04 (the NAT adapter is
   `admin01`'s way to the internet), and set the lab adapter's **DNS** to `10.10.10.1` so `admin01` can
   find lab names. Do this in **Settings > Network**.
8. See [09-squid.md](09-squid.md) later for the filtering proxy (not needed yet).

## Check it worked

- `https://10.10.10.1` answers from `admin01`.
- From `admin01`: `ping -c 3 10.10.10.1` works (the lab side), and `ping -c 3 example.com` works (the
  internet, through `admin01`'s own NAT adapter).
- In pfSense's dashboard, the WAN interface shows an address from VMware's NAT network and "up".
- `interfaces/lan/ipaddr` in the imported config is `10.10.10.1`; in the web page: **Interfaces > LAN**
  shows `10.10.10.1/24`.

> **Stop and check:** `admin01`'s `example.com` ping does not prove pfSense's internet link works, because
> `admin01` has its own NAT adapter. The proof is on pfSense's dashboard (WAN up, with an address) and
> in **Diagnostics > Ping** inside pfSense (ping `1.1.1.1`, then `example.com`). If the first works and the
> second does not, DNS is the problem, not the firewall.

## Evidence to capture

Save in `portfolio/evidence/02-pfsense/`:

| File | What it shows |
| --- | --- |
| `vm-settings.png` | The pfSense VM's two adapters and the network each is on |
| `console-menu.png` | pfSense's console menu with the WAN and LAN addresses |
| `render-output.txt` | The `render.py` command you ran and `ls -l ~/config.xml` (do **not** include the file's contents) |
| `dashboard.png` | pfSense's web dashboard, browser address bar visible, showing the interfaces |
| `ping-tests.txt` | `ping` to `10.10.10.1` from `admin01`, with the prompt |
| `pfsense-ping.png` | pfSense's **Diagnostics > Ping** reaching `1.1.1.1` and `example.com` |
| `evidence.md` | Your filled-in evidence log |

## Explain it in your own words

1. What does the firewall do for the lab network? Name at least three jobs.
2. What is the difference between the WAN and LAN interfaces, and how did you tell which adapter was which?
3. Why is the pfSense configuration generated from the inventory instead of typed in by hand?

## If it goes wrong

- Wrong interface names after import: redo the render with the correct `--wan`/`--lan` values and re-import.
- You can reach pfSense's page but nothing has internet: WAN and LAN are probably swapped. At the console
  menu choose option **1** (Assign Interfaces) and swap them.
- No internet on the LAN yet from machines other than `admin01`: expected until DHCP, DNS and the domain
  controller exist (guides 07 and 08).
- Locked out of the web page after the import: use the console menu to reset the password (option 3) or
  restore a snapshot. Take a snapshot of `pfsense01` now (`working-pfsense`) so you can always return here.

See `lab/pfsense/README.md` for more detail on the template.
