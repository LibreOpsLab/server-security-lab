# 15: Monitoring and logs

## What you will build

`mon01`: Prometheus, Alertmanager, Loki and Grafana. Every guest ships its logs here through Grafana Alloy.

**Time and difficulty:** 1.5 to 2.5 hours. Medium. Mostly a dashboard to explore, plus one experiment where
you break something on purpose to watch an alert fire.

> **Do this after guide 10.** Grafana's address (`grafana.lab.internal`) is served through Traefik on
> `docker01`, so the apps must exist first.

## Why

You cannot harden, or defend, what you cannot see. This guide gives every later security exercise something
to check: did monitoring notice?

> **What's going on:** Monitoring answers two questions. **Metrics** (Prometheus) are numbers sampled over
> time: CPU, memory, "is this machine up?". **Logs** (Loki) are the text each service writes about what it
> did: sign-ins, errors, connections. **Grafana** draws both as dashboards, and **Alertmanager** turns a
> rule such as "this host has been down for two minutes" into a notification. In the security weeks the
> logs are your evidence of what an attacker did.

## Before you start

- Guide 10 is complete (the apps and Traefik are up).
- Take a snapshot of `pve01` called `before-make-monitoring`.

## Steps

1. Read first. Open `lab/ansible/roles/monitoring/files/lab-rules.yml` and find the `HostDown` alert. Write
   down in plain words what it checks and for how long.
2. Build monitoring and ship logs from every guest:

   ```bash
   cd lab
   make monitoring
   ```

3. Open `https://grafana.lab.internal`, sign in, and find the **Lab overview** dashboard. Every guest
   should appear as reporting.
4. **Break something on purpose, then fix it.** Stop a harmless service on one guest and watch the alert:

   ```bash
   ssh -i ~/.ssh/lab_admin root@10.10.10.25 systemctl stop postfix
   ```

   Wait a couple of minutes, check Grafana or Alertmanager for an alert, then start it again with
   `systemctl start postfix`.

   > **Careful:** Only stop a service on a guest you built and only for the exercise. Write down the exact
   > commands you ran, so you can undo them. Do not do this on any machine that is not yours.

   > **Beginner tip:** If no `HostDown` alert appears, you stopped a _service_, not the whole host. Check
   > the alert rules: some fire only when the host disappears. Look at **Alerting** in Grafana or the
   > Alertmanager page for what is defined, then stop the right thing (or the whole guest from Proxmox's
   > web page) and write down what you learned.

## Check it worked

- `https://grafana.lab.internal` shows the "Lab overview" dashboard with every host reporting.
- Stopping a guest or the right service causes an alert within a couple of minutes in Grafana or
  Alertmanager.
- In Grafana's **Explore** page with the Loki data source, you can search for recent log lines from at least
  two different guests.

## Evidence to capture

> **Beginner tip:** `make evidence GUIDE=15` (from `lab/`) runs the read-only commands for you and saves them, stamped with your name, the date and the machine, in `auto-evidence.txt` in your evidence folder. Read it before you commit. It does not replace your screenshots, your notes or your own explanation.

Save in `portfolio/evidence/15-monitoring-and-logs/`:

| File                  | What it shows                                               |
| --------------------- | ----------------------------------------------------------- |
| `reading-notes.md`    | Your plain-words reading of the `HostDown` rule             |
| `make-monitoring.txt` | Output of `make monitoring` ending with the recap           |
| `dashboard.png`       | Lab overview with every host reporting and the time visible |
| `alert-firing.png`    | The alert firing after you broke something                  |
| `loki-logs.png`       | Log lines from two different guests in Grafana Explore      |
| `commands-run.txt`    | Exactly what you stopped and started, and when              |
| `evidence.md`         | Your filled-in evidence log                                 |

## Explain it in your own words

1. What is the difference between a metric and a log? Give one example of each from this lab.
2. How long did it take from breaking something to the alert? What decides that delay?
3. An attacker logs in as a user. Where would you look to see it?

## If it goes wrong

**Run this first:** `make preflight STAGE=monitoring`. It checks what this guide depends on and says what to fix.

- A guest is missing from the dashboard: confirm `log_shipper` ran for it (it is applied to every guest
  except `mon01` itself, which gets `monitoring` and `log_shipper` both).
- Grafana's page does not load: `make apps` must have been run (Traefik serves it), and `mon01` must be up.
  Test the address `10.10.10.24` directly if you suspect the proxy.
- The dashboard shows "No data": give it a few minutes, then check Prometheus's targets page on `mon01`.
- **Note:** Loki and the Alloy metrics endpoint have no login of their own. That is a deliberate weak
  default for the security loop, documented in `docs/instructor-weak-defaults.md`.

### Where to look

| What                    | Command or place                                                                    |
| ----------------------- | ----------------------------------------------------------------------------------- |
| Services on `mon01`     | `ssh root@10.10.10.24 systemctl status prometheus alertmanager loki grafana-server` |
| Prometheus targets      | Open `http://10.10.10.24:9090/targets` from `admin01`                               |
| Alerts                  | Open `http://10.10.10.24:9093` (Alertmanager)                                       |
| Log shipping on a guest | `ssh root@10.10.10.25 systemctl status alloy`                                       |
| Grafana's log           | `ssh root@10.10.10.24 journalctl -u grafana-server -n 50 --no-pager`                |
