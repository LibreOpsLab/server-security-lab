import json
from pathlib import Path

import pytest

jinja2 = pytest.importorskip("jinja2")
yaml = pytest.importorskip("yaml")

LAB = Path(__file__).parents[2] / "lab"
VARS = yaml.safe_load((LAB / "inventory/group_vars/all.yml").read_text())
MON = LAB / "ansible/roles/monitoring"
SHIP = LAB / "ansible/roles/log_shipper"


def render(role_dir, name, **extra):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(role_dir / "templates"), undefined=jinja2.StrictUndefined)
    env.globals["lookup"] = lambda *a, **k: "SECRET-FROM-FILE"
    return env.get_template(name).render(**{**VARS, "lab_secrets_dir": "/s", "inventory_hostname": "mon01", **extra})


def test_prometheus_scrapes_every_proxmox_guest_exporter():
    cfg = yaml.safe_load(render(MON, "prometheus.yml.j2"))
    targets = {t for job in cfg["scrape_configs"] for sc in job.get("static_configs", []) for t in sc["targets"]}
    guests = [h["ip"] for h in VARS["lab_hosts"].values() if h["kind"] in ("lxc", "vm")]
    assert all(f"{ip}:9100" in targets for ip in guests)
    assert "/etc/prometheus/rules/lab.yml" in cfg["rule_files"]


def test_alert_rules_cover_down_disk_and_failed_ssh_logins():
    rules = yaml.safe_load((MON / "files/lab-rules.yml").read_text())
    alerts = {r["alert"]: r for g in rules["groups"] for r in g["rules"]}
    assert {"HostDown", "DiskAlmostFull", "SshFailedLogins"} <= set(alerts)
    assert "loki_process_custom_ssh_failed_logins_total" in alerts["SshFailedLogins"]["expr"]
    assert all(a["labels"]["severity"] for a in alerts.values())


def test_dashboard_is_valid_json_with_the_basic_panels():
    dash = json.loads((MON / "files/lab-overview.json").read_text())
    titles = {p["title"] for p in dash["panels"]}
    assert {"Hosts up", "CPU used", "Memory used"} <= titles


def test_grafana_has_both_datasources_and_the_admin_password_comes_from_the_secret():
    ds = yaml.safe_load(render(MON, "datasources.yml.j2"))["datasources"]
    assert {d["type"] for d in ds} == {"prometheus", "loki"}
    ini = (MON / "templates/grafana-admin.ini.j2").read_text()
    assert "grafana_admin_password" in ini and "grafana.lab.internal" in ini.replace("{{ lab_domain }}", "lab.internal")


def test_alloy_on_every_guest_ships_ssh_journal_logs_and_counts_failed_logins():
    cfg = render(SHIP, "config.alloy.j2", inventory_hostname="files01")
    assert "loki.source.journal" in cfg and "Failed password" in cfg and "ssh_failed_logins_total" in cfg
    assert f"http://{VARS['lab_hosts']['mon01']['ip']}:3100/loki/api/v1/push" in cfg
    assert "loki.source.syslog" not in cfg  # only the monitoring guest listens for firewall logs


def test_alloy_on_mon01_also_listens_for_pfsense_syslog_on_1514():
    cfg = render(SHIP, "config.alloy.j2", inventory_hostname="mon01")
    assert "loki.source.syslog" in cfg and f"{VARS['lab_hosts']['mon01']['ip']}:1514" in cfg


def test_loki_config_is_valid_yaml_with_filesystem_storage():
    cfg = yaml.safe_load(render(MON, "loki.yml.j2"))
    assert cfg["common"]["storage"]["filesystem"]["chunks_directory"].startswith("/var/lib/loki")


def test_grafana_repository_is_signed_and_shared_by_both_roles():
    repo = (LAB / "ansible/roles/grafana_repo/tasks/main.yml").read_text()
    assert "signed-by" in repo and "apt.grafana.com" in repo
    for role in (MON, SHIP):
        assert "grafana_repo" in (role / "meta/main.yml").read_text()


def test_playbook_builds_the_monitoring_guest_then_ships_logs_from_every_other_guest():
    play = (LAB / "ansible/playbooks/60-monitoring.yml").read_text()
    assert "monitoring" in play and "log_shipper" in play and "!monitoring" in play


def test_listeners_bind_to_the_guests_own_address_not_every_interface():
    cfg = render(SHIP, "config.alloy.j2", inventory_hostname="mon01")
    assert f"{VARS['lab_hosts']['mon01']['ip']}:1514" in cfg and "0.0.0.0" not in cfg
    tasks = (SHIP / "tasks/main.yml").read_text()
    assert "lab_hosts[inventory_hostname].ip" in tasks and "0.0.0.0" not in tasks
    ini = (MON / "templates/grafana-admin.ini.j2").read_text()
    assert "http_addr = {{ lab_hosts['mon01'].ip }}" in ini


def test_the_open_telemetry_endpoints_are_recorded_as_deliberate_weak_defaults():
    loki = (MON / "templates/loki.yml.j2").read_text()
    assert "auth_enabled: false" in loki and "deliberate" in loki.lower()
