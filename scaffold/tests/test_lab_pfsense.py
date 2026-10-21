import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

pytest.importorskip("jinja2")
pytest.importorskip("yaml")

REPO = Path(__file__).parents[2]
PF = REPO / "lab" / "pfsense"


def render(*args):
    r = subprocess.run([sys.executable, str(PF / "render.py"), *args], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout


def test_render_is_wellformed_xml_and_uses_the_interface_flags():
    root = ET.fromstring(render("--wan", "em0", "--lan", "em1", "--hostname", "pfsense01"))
    assert root.tag == "pfsense"
    assert root.find("interfaces/wan/if").text == "em0" and root.find("interfaces/lan/if").text == "em1"
    assert root.find("system/hostname").text == "pfsense01"


def test_lan_dhcp_dns_and_domain_come_from_the_inventory():
    root = ET.fromstring(render())
    assert root.find("interfaces/lan/ipaddr").text == "10.10.10.1" and root.find("interfaces/lan/subnet").text == "24"
    assert root.find("dhcpd/lan/range/from").text == "10.10.10.100" and root.find("dhcpd/lan/range/to").text == "10.10.10.199"
    assert [e.text for e in root.findall("dhcpd/lan/dnsserver")] == ["10.10.10.21", "10.10.10.1"]
    assert root.find("dhcpd/lan/domain").text == "lab.internal"
    assert "forward-addr: 10.10.10.21" in root.find("unbound/custom_options").text


def test_allow_lan_to_any_rule_is_present_as_a_deliberate_weak_default():
    text = render()
    root = ET.fromstring(text)
    rules = root.findall("filter/rule")
    assert any(r.find("type").text == "pass" and r.find("destination/any") is not None for r in rules)
    assert "deliberate" in text.lower()


def test_no_passwords_or_hashes_in_the_template():
    text = render().lower()
    for word in ("<password", "bcrypt", "<authorizedkeys", "<pre-shared-key"):
        assert word not in text


def test_renders_the_same_every_time():
    assert render() == render()


def test_missing_inventory_value_fails_loudly(tmp_path):
    r = subprocess.run([sys.executable, str(PF / "render.py"), "--vars", str(tmp_path / "nope.yml")], capture_output=True, text=True)
    assert r.returncode != 0


def test_squid_doc_states_the_agreed_settings():
    doc = (PF / "squid.md").read_text()
    assert "3128" in doc and "no SSL" in doc and "CE" in doc and "curl -x" in doc
