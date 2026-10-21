"""nmap `-oX` output to findings: one per open port, with the detected service and version."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from ..findings import Finding

CLEARTEXT = {"telnet", "ftp", "rsh", "rlogin", "tftp", "vnc", "pop3", "imap"}


def parse_nmap_xml(text: str) -> list[Finding]:
    out = []
    for port in ET.fromstring(text).iter("port"):
        state = port.find("state")
        if state is None or state.get("state") != "open":
            continue
        svc = port.find("service")
        name = svc.get("name", "unknown") if svc is not None else "unknown"
        version = (
            " ".join(filter(None, (svc.get("product"), svc.get("version"))))
            if svc is not None
            else ""
        )
        pid, proto = port.get("portid"), port.get("protocol")
        out.append(
            Finding(
                f"nmap:{pid}/{proto}",
                "service",
                f"Open port {pid}/{proto} ({name})",
                "medium" if name in CLEARTEXT else "info",
                version or "version not detected",
            )
        )
    return out
