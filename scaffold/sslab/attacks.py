"""The fixed attack set (see docs/attack-set.md). Each attack is a command plus a parser into findings.

Runner contract: return stdout whatever the exit status (a refused login is a result, not a failure);
raise only when the tool cannot run at all. That is what lands an attack in `not_run`.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .collectors import utc_now
from .collectors.nmap import parse_nmap_xml
from .findings import Finding, Run
from .scope import require_in_scope

DATA = Path(__file__).parent / "data"


@dataclass(frozen=True)
class Attack:
    id: str
    title: str
    layer: str
    tool: str
    command: Callable[[str], list[str]]
    parse: Callable[[str], list[Finding]]


def _f(attack: str, detail: str, layer: str, title: str, severity: str, text: str = "") -> Finding:
    return Finding(f"attack:{attack}:{detail}", layer, title, severity, text)


def _enum(out: str) -> list[Finding]:
    return [
        Finding(f.id.replace("nmap:", "attack:enum-services:"), f.layer, f.title, f.severity, f.detail)
        for f in parse_nmap_xml(out)
    ]


def _ssh(out: str) -> list[Finding]:
    hits = re.findall(r"login:\s*(\S+)\s+password:\s*(\S+)", out)
    return [_f("ssh-weak-creds", user, "identity", f"SSH login works for '{user}' with a guessable password", "high", f"password: {pw}") for user, pw in hits]


_WEB_HEADERS = {
    "strict-transport-security": ("no-hsts", "No HSTS header", "medium"),
    "x-frame-options": ("no-xfo", "No X-Frame-Options header", "low"),
    "content-security-policy": ("no-csp", "No Content-Security-Policy header", "low"),
    "x-content-type-options": ("no-nosniff", "No X-Content-Type-Options header", "low"),
}


def _web(out: str) -> list[Finding]:
    low = out.lower()
    found = [_f("web-basics", k, "service", t, s) for h, (k, t, s) in _WEB_HEADERS.items() if f"{h}:" not in low]
    banner = re.search(r"^server:\s*(\S*\d\S*)", out, re.I | re.M)  # a banner containing a version number
    if banner:
        found.append(_f("web-basics", "server-banner", "service", "Server banner reveals its version", "low", banner.group(1)))
    return found


def _mail(out: str) -> list[Finding]:
    found = []
    if re.search(r"is an open relay", out) and "doesn't seem to be an open relay" not in out:
        found.append(_f("mail-basics", "open-relay", "service", "Mail server relays for strangers", "high"))
    if re.search(r"smtp-commands:.*\bVRFY\b", out):
        found.append(_f("mail-basics", "vrfy", "service", "VRFY lets anyone confirm which users exist", "medium"))
    return found


def _anon(out: str) -> list[Finding]:
    return [
        _f("anon-directory", name, "identity", f"Share '{name}' is visible without logging in", "medium")
        for name in re.findall(r"^\s*(\S+)\s+Disk\b", out, re.M)
    ]


ATTACKS: list[Attack] = [
    Attack("enum-services", "Service enumeration", "service", "nmap", lambda ip: ["nmap", "-sV", "-p-", "-oX", "-", ip], _enum),
    Attack("ssh-weak-creds", "Weak SSH credentials", "identity", "hydra",
           lambda ip: ["hydra", "-L", str(DATA / "users.txt"), "-P", str(DATA / "passwords.txt"), "-t", "2", f"ssh://{ip}"], _ssh),
    Attack("web-basics", "Web headers", "service", "curl", lambda ip: ["curl", "-sI", "--max-time", "10", f"http://{ip}/"], _web),
    Attack("mail-basics", "Mail relay and VRFY", "service", "nmap",
           lambda ip: ["nmap", "-p25", "--script", "smtp-open-relay,smtp-commands", ip], _mail),
    Attack("anon-directory", "Anonymous share listing", "identity", "smbclient", lambda ip: ["smbclient", "-N", "-L", f"//{ip}"], _anon),
]


def run_attacks(
    target: str,
    nets: list[ipaddress.IPv4Network],
    label: str,
    student: str,
    fork: str,
    runner: Callable[[list[str]], str],
    now: Callable[[], str] = utc_now,
) -> Run:
    ip = require_in_scope(target, nets)  # before any packet is sent
    run = Run(label, "attack-set", target, student, fork, ", ".join(str(n) for n in nets), now())
    for attack in ATTACKS:
        try:
            found = attack.parse(runner(attack.command(ip)))
        except Exception:  # tool missing, or output we cannot read: not run, never "clean"
            run.not_run.append(attack.id)
            continue
        run.findings += found
    return run
