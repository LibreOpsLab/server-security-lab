"""Lynis `lynis-report.dat` to findings. Warnings are high, suggestions medium."""

from __future__ import annotations

from ..findings import Finding

_LAYERS = {"NETW": "network", "FIRE": "network", "AUTH": "identity", "ACCT": "identity"}


def _layer(test_id: str) -> str:
    return _LAYERS.get(test_id.split("-", 1)[0], "host")


def parse_lynis_report(text: str) -> list[Finding]:
    out = []
    for line in text.splitlines():
        for prefix, severity in (("warning[]=", "high"), ("suggestion[]=", "medium")):
            if line.startswith(prefix):
                test_id, title, detail, *_ = line[len(prefix) :].split("|") + ["", ""]
                out.append(
                    Finding(
                        f"lynis:{test_id}",
                        _layer(test_id),
                        title,
                        severity,
                        detail if detail != "-" else "",
                    )
                )
    return out


def parse_lynis_index(text: str) -> int | None:
    for line in text.splitlines():
        if line.startswith("hardening_index="):
            try:
                return int(line.split("=", 1)[1])
            except (
                ValueError
            ):  # an interrupted audit can leave this empty; the findings are still real
                return None
    return None
