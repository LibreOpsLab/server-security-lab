"""A blank table for the manager conversation: what each finding means in business terms, for the student
to fill in themselves. Never prefilled with an answer, only with the finding."""

from __future__ import annotations

from .compare import ORDER, Comparison, LABELS
from .report import esc, html_page, md


def impact_table(c: Comparison) -> str:
    out = [
        f"# Business impact: {c.before.tool} on {c.before.host}", "",
        "Fill in the two right-hand columns yourself, in plain business language: money, customers, trust, "
        "downtime, legal duties. No technical terms.", "",
        "| State | Finding | What could happen | What it means for the business |",
        "| --- | --- | --- | --- |",
    ]
    for r in sorted(c.rows, key=lambda r: ORDER.index(r.state)):
        out.append(f"| {LABELS.get(r.state, r.state)} | {md(r.title)} |  |  |")
    return "\n".join(out) + "\n"


def impact_table_html(c: Comparison) -> str:
    body = [f"<h1>Business impact: {esc(c.before.tool)} on {esc(c.before.host)}</h1>",
            "<table><thead><tr><th>State</th><th>Finding</th><th>What could happen</th>"
            "<th>What it means for the business</th></tr></thead><tbody>"]
    for r in sorted(c.rows, key=lambda r: ORDER.index(r.state)):
        body.append(f"<tr><td>{esc(LABELS.get(r.state, r.state))}</td><td>{esc(r.title)}</td><td></td><td></td></tr>")
    body.append("</tbody></table>")
    return html_page(f"Business impact {c.before.host}", "".join(body))
