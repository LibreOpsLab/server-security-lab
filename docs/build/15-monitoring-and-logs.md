# 15: Monitoring and logs

## What you will build

`mon01`: Prometheus, Alertmanager, Loki and Grafana. Every guest ships its logs here through Grafana Alloy.

## Why

You cannot harden, or defend, what you cannot see. This guide gives every later security exercise something
to check: did monitoring notice?

## Steps

```bash
cd lab
make monitoring
```

## Check it worked

- `https://grafana.lab.internal` shows the "Lab overview" dashboard with every host reporting.
- Stop a service on any guest; the `HostDown` alert fires within a couple of minutes in Grafana or
  Alertmanager.

## If it goes wrong

- A guest is missing from the dashboard: confirm `log_shipper` ran for it (it is applied to every guest
  except `mon01` itself, which gets `monitoring` and `log_shipper` both).
- **Note:** Loki and the Alloy metrics endpoint have no login of their own. That is a deliberate weak
  default for the security loop, documented in `docs/instructor-weak-defaults.md`.
