"""Run one tool against one in-scope target and return a Run. A tool that cannot run goes in `not_run`."""

from __future__ import annotations

import ipaddress
from datetime import datetime, timezone
from typing import Callable

from ..findings import Run
from ..scope import require_in_scope
from .lynis import parse_lynis_index, parse_lynis_report
from .nmap import parse_nmap_xml
from .windows import parse_windows_audit

# Placeholder until the lab validation picks the Windows audit tool (see docs/instructor-weak-defaults.md).
_WIN_CMD = "powershell -NoProfile -File C:\\audit\\run-audit.ps1"

COMMANDS: dict[str, Callable[[str], list[str]]] = {
    "lynis": lambda ip: ["ssh", ip, "sudo lynis audit system --quiet >/dev/null 2>&1; sudo cat /var/log/lynis-report.dat"],
    "nmap": lambda ip: ["nmap", "-sV", "-oX", "-", ip],
    "windows": lambda ip: ["ssh", ip, _WIN_CMD],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def collect(
    tool: str,
    target: str,
    nets: list[ipaddress.IPv4Network],
    label: str,
    student: str,
    fork: str,
    runner: Callable[[list[str]], str],
    now: Callable[[], str] = utc_now,
) -> Run:
    if tool not in COMMANDS:
        raise ValueError(f"unknown tool {tool!r}; known: {', '.join(COMMANDS)}")
    ip = require_in_scope(target, nets)  # raises ScopeError before anything runs
    run = Run(label, tool, target, student, fork, ", ".join(str(n) for n in nets), now())
    try:
        out = runner(COMMANDS[tool](ip))
        if tool == "lynis":
            findings, index = parse_lynis_report(out), parse_lynis_index(out)
            if index is not None:
                run.metrics["hardening_index"] = str(index)
        elif tool == "nmap":
            findings = parse_nmap_xml(out)
        else:
            findings = parse_windows_audit(out)
    except Exception:  # missing tool, non-zero exit, or output we cannot read: record, never count as closed
        run.not_run.append(tool)
        run.metrics.clear()
        return run
    run.findings = findings
    return run
