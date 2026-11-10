#!/usr/bin/env python3
"""Write docs/company/org-chart.md from the manager column of lab/data/users.csv.

Usage: scripts/gen-org-chart.py [--check]
  --check   exit 1 if the file on disk is not what the CSV produces (used by the tests; table alignment is ignored)

Only people (employee type other than "Shared mailbox" or "Shared account") are drawn. The chart is Mermaid, plus the
same tree as a list for readers who cannot render Mermaid.
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "lab" / "data" / "users.csv"
OUT = ROOT / "docs" / "company" / "org-chart.md"
NOT_PEOPLE = {"Shared mailbox", "Shared account"}


def read():
    lines = [ln for ln in CSV.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    return list(csv.DictReader(lines))


def node(user):
    return "n_" + user.replace(".", "_").replace("-", "_")


def build(rows=None):
    rows = rows if rows is not None else read()
    people = [r for r in rows if r["employee_type"] not in NOT_PEOPLE]
    mailboxes = [r for r in rows if r["employee_type"] == "Shared mailbox"]
    by_user = {r["username"]: r for r in rows}
    perth = "Perth head office"
    md = [
        "# Boab Ridge Mining Services: organisation chart",
        "",
        f"Generated from the `manager` column of `lab/data/users.csv` by `scripts/gen-org-chart.py`. {len(people)} people, all fictional. "
        "Dark boxes are the Perth head office, light boxes the remote site office.",
        "",
        "```mermaid",
        "flowchart TB",
    ]
    for r in people:
        cls = "perth" if r["office"] == perth else "site"
        md.append(f'  {node(r["username"])}["{r["display_name"]}<br/>{r["title"]}"]:::{cls}')
    for r in people:
        if r["manager"]:
            md.append(f'  {node(r["manager"])} --> {node(r["username"])}')
    md += [
        "  classDef perth fill:#8547AD,stroke:#323E48,color:#fff",
        "  classDef site fill:#E6D9EF,stroke:#323E48,color:#323E48",
        "```",
        "",
        "## The same chart as a list",
        "",
    ]
    kids = {}
    for r in people:
        kids.setdefault(r["manager"], []).append(r["username"])

    def walk(u, depth):
        r = by_user[u]
        place = "Perth" if r["office"] == perth else "site"
        md.append("  " * depth + f'- **{r["display_name"]}**, {r["title"]} ({r["department"]}, {place})')
        for k in kids.get(u, []):
            walk(k, depth + 1)

    for root in kids.get("", []):
        walk(root, 0)
    md += ["", "## Shared mailboxes", "", "| Mailbox | Name | Responsible person |", "| --- | --- | --- |"]
    for r in mailboxes:
        m = by_user[r["manager"]]
        md.append(f'| `{r["username"]}@boab.lab` | {r["display_name"]} | {m["display_name"]}, {m["title"]} |')
    md += ["", "Staff who answer a shared mailbox sign in to its account (see `docs/build/12-mail.md`).", ""]
    return "\n".join(md)


if __name__ == "__main__":
    text = build()
    if "--check" in sys.argv:
        # The chart and list must match exactly. The table below them may be re-aligned by a Markdown formatter,
        # so only its rows' contents are compared.
        cut = "## Shared mailboxes"
        disk = OUT.read_text(encoding="utf-8")
        cells = lambda t: [[c.strip() for c in ln.strip("|").split("|")] for ln in t.split(cut)[1].splitlines() if ln.startswith("| `")]
        same = disk.split(cut)[0] == text.split(cut)[0] and cells(disk) == cells(text)
        sys.exit(0 if same else 1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")
