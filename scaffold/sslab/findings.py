"""The common record every collector produces and every report and comparison reads."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

LAYERS = ("network", "host", "service", "identity")
SEVERITIES = ("info", "low", "medium", "high")


@dataclass(frozen=True)
class Finding:
    id: str
    layer: str
    title: str
    severity: str
    detail: str


@dataclass
class Run:
    label: str  # "default" or "hardened"
    tool: str
    host: str
    student: str
    fork: str
    lab_range: str
    started: str  # UTC, ISO 8601, e.g. 2026-11-16T01:02:03Z
    findings: list[Finding] = field(default_factory=list)
    not_run: list[str] = field(default_factory=list)


def _stem(run: Run) -> str:
    stamp = run.started.replace(":", "").replace("-", "")
    return f"{run.label}-{run.tool}-{run.host}-{stamp}"


def save_run(run: Run, outdir: Path) -> Path:
    """Write the run as JSON. Never overwrites: a clash gets -2, -3, ..."""
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{_stem(run)}.json"
    n = 2
    while path.exists():
        path = outdir / f"{_stem(run)}-{n}.json"
        n += 1
    path.write_text(json.dumps(asdict(run), indent=2) + "\n", encoding="utf-8")
    return path


def load_run(path: Path) -> Run:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["findings"] = [Finding(**f) for f in data["findings"]]
    return Run(**data)
