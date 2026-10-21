import ipaddress
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

LAB = Path(__file__).parents[2] / "lab"
VARS = yaml.safe_load((LAB / "inventory" / "group_vars" / "all.yml").read_text())
HOSTS = VARS["lab_hosts"]

# The design's exact guests and addresses (docs/design/lab-build-design.md).
EXPECTED = {
    "pfsense01": "10.10.10.1", "pve01": "10.10.10.5", "admin01": "10.10.10.10", "win-client01": "10.10.10.11",
    "samba-dc01": "10.10.10.21", "auth01": "10.10.10.22", "radius01": "10.10.10.23", "mon01": "10.10.10.24",
    "mail01": "10.10.10.25", "files01": "10.10.10.26", "pbs01": "10.10.10.27", "docker01": "10.10.10.30",
}


def test_names_and_addresses_match_the_design():
    assert {n: h["ip"] for n, h in HOSTS.items()} == EXPECTED


def test_ips_unique_and_in_subnet():
    net = ipaddress.ip_network(VARS["lab_subnet"])
    ips = [h["ip"] for h in HOSTS.values()]
    assert len(ips) == len(set(ips))
    assert all(ipaddress.ip_address(i) in net for i in ips)


def test_no_guest_sits_in_the_dhcp_pool():
    for name, h in HOSTS.items():
        last = int(h["ip"].split(".")[-1])
        assert not 100 <= last <= 199, name


def test_ram_within_budget():
    budget = VARS["ram_budget_mb"]
    vmware = sum(h["ram_mb"] for h in HOSTS.values() if h["kind"] == "vmware")
    proxmox = sum(h["ram_mb"] for h in HOSTS.values() if h["kind"] in ("lxc", "vm"))
    assert vmware <= budget["vmware"], vmware
    assert proxmox <= budget["proxmox"], proxmox


def test_proxmox_guests_have_unique_vmids():
    ids = [h["vmid"] for h in HOSTS.values() if h["kind"] in ("lxc", "vm")]
    assert len(ids) == len(set(ids)) == 8


def test_samba_dc_is_privileged_and_flagged():
    assert VARS["samba_dc_privileged"] is True


def test_only_windows_is_optional():
    assert [n for n, h in HOSTS.items() if h.get("optional")] == ["win-client01"]


def test_hosts_yml_groups_cover_every_proxmox_guest_without_ips():
    inv = yaml.safe_load((LAB / "inventory" / "hosts.yml").read_text())
    names = set()

    def walk(node):
        names.update((node.get("hosts") or {}).keys())
        for child in (node.get("children") or {}).values():
            walk(child)

    walk(inv["all"])
    guests = {n for n, h in HOSTS.items() if h["kind"] in ("lxc", "vm")}
    assert guests <= names and "pve01" in names
    assert "10.10.10." not in (LAB / "inventory" / "hosts.yml").read_text()  # addresses live in one place


def test_ldap_names_are_derived_consistently_from_the_domain():
    dc = ",".join(f"DC={part}" for part in VARS["lab_domain"].split("."))
    assert VARS["lab_base_dn"] == dc
    assert VARS["lab_users_dn"] == f"OU=LabUsers,{dc}" and VARS["lab_service_dn"] == f"OU=LabService,{dc}"
    assert VARS["lab_ldap_uri"] == f"ldaps://samba-dc01.{VARS['lab_domain']}"


def test_certificates_cover_the_aliases_and_wildcard_for_the_web_tier():
    certs = {c["cn"]: c["san"] for c in VARS["lab_certificates"]}
    assert certs["mail01.lab.internal"].count("DNS:") >= 2 and "DNS:*.lab.internal" in certs["docker01.lab.internal"]
    assert {"mail01.lab.internal", "auth01.lab.internal", "docker01.lab.internal", "mon01.lab.internal"} <= set(certs)


def test_every_service_account_secret_is_one_gen_secrets_creates():
    gen = (LAB.parent / "scripts" / "gen-secrets.sh").read_text()
    accounts = VARS["lab_service_accounts"]
    assert {a["name"] for a in accounts} >= {"svc-mail", "svc-authelia"}
    assert all(a["secret"] in gen for a in accounts)
