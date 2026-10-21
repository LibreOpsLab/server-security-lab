"""Windows audit CSV to findings. Columns: Id,Name,Severity,Status. Only `Failed` rows become findings.

The audit tool itself is chosen in the lab validation (see docs/instructor-weak-defaults.md); this parser matches a HardeningKitty-style list.
"""

from __future__ import annotations

import csv
import io

from ..findings import SEVERITIES, Finding


def parse_windows_audit(csv_text: str) -> list[Finding]:
    rows = (
        r
        for r in csv.DictReader(io.StringIO(csv_text))
        if r.get("Id") and not r["Id"].startswith("#")
    )
    out = []
    for r in rows:
        if r["Status"].strip().lower() != "failed":
            continue
        sev = r["Severity"].strip().lower()
        out.append(
            Finding(
                f"win:{r['Id']}",
                "host",
                r["Name"],
                sev if sev in SEVERITIES else "medium",
                "",
            )
        )
    return out
