"""Compare a "default" run with a "hardened" run of the same tool on the same host."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .findings import SEVERITIES, Run, file_stem
from .report import esc, html_page

# Gaps first: what is still open or new matters more than what was closed.
ORDER = ("unchanged", "new", "reduced", "not_compared", "closed")
LABELS = {"not_compared": "not compared"}
CAUTION = "The after run recorded no findings: confirm the tool ran before reading that as clean."


@dataclass
class Row:
    id: str
    title: str
    layer: str
    before: str | None  # severity in the default run
    after: str | None  # severity in the hardened run
    state: str  # closed | reduced | unchanged | new | not_compared


@dataclass
class Comparison:
    before: Run
    after: Run
    rows: list[Row]


def _not_run_after(after: Run, finding_id: str) -> bool:
    if after.tool in after.not_run:
        return True
    parts = finding_id.split(":")
    return parts[0] == "attack" and len(parts) > 1 and parts[1] in after.not_run


def compare(before: Run, after: Run) -> Comparison:
    if before.host != after.host or before.tool != after.tool:
        raise ValueError(f"different hosts or tools: {before.tool}@{before.host} vs {after.tool}@{after.host}")
    if not before.findings:
        raise ValueError("the before run has no findings: nothing to compare. Check the tool ran in week 12")
    a = {f.id: f for f in after.findings}
    rows = []
    for f in before.findings:
        if _not_run_after(after, f.id):
            state, now = "not_compared", None
        elif f.id not in a:
            state, now = "closed", None
        else:
            now = a[f.id].severity
            state = "reduced" if SEVERITIES.index(now) < SEVERITIES.index(f.severity) else "unchanged"
        rows.append(Row(f.id, f.title, f.layer, f.severity, now, state))
    known = {f.id for f in before.findings}
    rows += [Row(f.id, f.title, f.layer, None, f.severity, "new") for f in after.findings if f.id not in known]
    rows.sort(key=lambda r: ORDER.index(r.state))
    return Comparison(before, after, rows)


def _summary(c: Comparison) -> str:
    n = {s: sum(r.state == s for r in c.rows) for s in ORDER}
    return ", ".join(f"{n[s]} {LABELS.get(s, s)}" for s in ("closed", "reduced", "unchanged", "new", "not_compared"))


def _metrics(c: Comparison) -> list[str]:
    keys = list(dict.fromkeys([*c.before.metrics, *c.after.metrics]))
    return [f"{k}: {c.before.metrics.get(k, '?')} → {c.after.metrics.get(k, '?')}" for k in keys]


def _title(c: Comparison) -> str:
    return f"Comparison: {c.before.tool} on {c.before.host}"


def render_comparison_markdown(c: Comparison) -> str:
    b, a = c.before, c.after
    out = [f"# {_title(c)}", "", _summary(c), ""]
    if not a.findings and not a.not_run:
        out += [CAUTION, ""]
    out += [f"- **Student:** {b.student} ({b.fork})", f"- **Before:** {b.label}, {b.started}",
            f"- **After:** {a.label}, {a.started}", *[f"- {m}" for m in _metrics(c)], ""]
    out += ["| State | Layer | Finding | Before | After |", "| --- | --- | --- | --- | --- |"]
    out += [f"| {LABELS.get(r.state, r.state)} | {r.layer} | {r.title} | {r.before or '-'} | {r.after or '-'} |" for r in c.rows]
    out.append("")
    if a.not_run:
        out += ["## Not run in the after run", "", *[f"- {t}" for t in a.not_run], ""]
    return "\n".join(out)


def render_comparison_html(c: Comparison) -> str:
    b, a = c.before, c.after
    body = [f"<h1>{esc(_title(c))}</h1><p><strong>{esc(_summary(c))}</strong></p>"]
    if not a.findings and not a.not_run:
        body.append(f"<p>{esc(CAUTION)}</p>")
    body.append(f'<p class="meta">{esc(b.student)} ({esc(b.fork)}) · before: {esc(b.label)} {esc(b.started)} · after: {esc(a.label)} {esc(a.started)}'
                + "".join(f" · {esc(m)}" for m in _metrics(c)) + "</p>")
    body.append("<table><thead><tr><th>State</th><th>Layer</th><th>Finding</th><th>Before</th><th>After</th></tr></thead><tbody>")
    body += [f"<tr><td>{esc(LABELS.get(r.state, r.state))}</td><td>{esc(r.layer)}</td><td>{esc(r.title)}</td><td>{esc(r.before or '-')}</td><td>{esc(r.after or '-')}</td></tr>" for r in c.rows]
    body.append("</tbody></table>")
    if a.not_run:
        body.append("<h2>Not run in the after run</h2><ul>" + "".join(f"<li>{esc(t)}</li>" for t in a.not_run) + "</ul>")
    return html_page(_title(c), "".join(body))


def write_comparison(c: Comparison, outdir: Path) -> tuple[Path, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    stem = f"compare-{c.before.tool}-{c.before.host}-{file_stem(c.after).rsplit('-', 1)[-1]}"
    md, html = outdir / f"{stem}.md", outdir / f"{stem}.html"
    n = 2
    while md.exists() or html.exists():
        md, html = outdir / f"{stem}-{n}.md", outdir / f"{stem}-{n}.html"
        n += 1
    md.write_text(render_comparison_markdown(c), encoding="utf-8")
    html.write_text(render_comparison_html(c), encoding="utf-8")
    return md, html
