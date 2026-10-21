"""Markdown and HTML reports for one run. Inline CSS only, no external requests."""

from __future__ import annotations

import html as _html
from pathlib import Path

from .findings import LAYERS, SEVERITIES, Finding, Run, file_stem

NO_FINDINGS = "No findings recorded. This is not the same as a clean result."

CSS = """
:root{--bg:#fff;--fg:#1F2933;--muted:#5b6770;--card:#f5f5f5;--line:#dad9d7;--accent:#4F46B5;--onaccent:#fff}
@media (prefers-color-scheme: dark){:root{--bg:#1d2329;--fg:#e8eaec;--muted:#a7b0b7;--card:#272f36;--line:#3b454d;--accent:#a9a0f2;--onaccent:#1d2329}}
body{font-family:Arial,Helvetica,sans-serif;background:var(--bg);color:var(--fg);margin:0;padding:1.5rem;line-height:1.5}
main{max-width:60rem;margin:0 auto}h1{color:var(--accent);margin-top:0}
table{border-collapse:collapse;width:100%;margin:.5rem 0 1.5rem}
th{background:var(--accent);color:var(--onaccent);text-align:left}
th,td{padding:.5rem .6rem;border:1px solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:var(--card)}.meta{color:var(--muted)}
"""


_MD_SPECIAL = str.maketrans({c: "\\" + c for c in "\\`*[]|"})


def md(text: str) -> str:
    """Make untrusted text (banners, tool output) inert in Markdown: one line, no tags, links or tables."""
    one_line = " ".join(str(text).split())
    return one_line.replace("<", "&lt;").replace(">", "&gt;").translate(_MD_SPECIAL)


def esc(text: str) -> str:
    return _html.escape(text, quote=True)


def html_page(title: str, body: str) -> str:
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{esc(title)}</title><style>{CSS}</style></head><body><main>{body}</main></body></html>\n"
    )


def _sorted(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda f: -SEVERITIES.index(f.severity))


def _meta(run: Run) -> list[tuple[str, str]]:
    return [
        ("Student", run.student), ("Repository", run.fork), ("Host", run.host), ("Lab range", run.lab_range),
        ("Label", run.label), ("Tool", run.tool), ("Started (UTC)", run.started),
    ]


def render_markdown(run: Run) -> str:
    out = [f"# {md(run.tool)} report: {md(run.host)} ({md(run.label)})", ""]
    out += [f"- **{k}:** {md(v)}" for k, v in _meta(run)]
    out += [f"- **{md(k)}:** {md(v)}" for k, v in run.metrics.items()]
    out.append("")
    if not run.findings:
        out += [NO_FINDINGS, ""]
    for layer in LAYERS:
        rows = _sorted([f for f in run.findings if f.layer == layer])
        if not rows:
            continue
        out += [f"## {layer.capitalize()}", "", "| Severity | Finding | Detail |", "| --- | --- | --- |"]
        out += [f"| {md(f.severity)} | {md(f.title)} | {md(f.detail)} |" for f in rows]
        out.append("")
    if run.not_run:
        out += ["## Not run", "", *[f"- {md(t)}" for t in run.not_run], ""]
    return "\n".join(out)


def render_html(run: Run) -> str:
    body = [f"<h1>{esc(run.tool)} report: {esc(run.host)} ({esc(run.label)})</h1>"]
    body.append('<p class="meta">' + " · ".join(f"{esc(k)}: {esc(v)}" for k, v in _meta(run) + list(run.metrics.items())) + "</p>")
    if not run.findings:
        body.append(f"<p>{esc(NO_FINDINGS)}</p>")
    for layer in LAYERS:
        rows = _sorted([f for f in run.findings if f.layer == layer])
        if not rows:
            continue
        body.append(f"<h2>{layer.capitalize()}</h2><table><thead><tr><th>Severity</th><th>Finding</th><th>Detail</th></tr></thead><tbody>")
        body += [f"<tr><td>{esc(f.severity)}</td><td>{esc(f.title)}</td><td>{esc(f.detail)}</td></tr>" for f in rows]
        body.append("</tbody></table>")
    if run.not_run:
        body.append("<h2>Not run</h2><ul>" + "".join(f"<li>{esc(t)}</li>" for t in run.not_run) + "</ul>")
    return html_page(f"{run.tool} {run.host} {run.label}", "".join(body))


def write_reports(run: Run, outdir: Path) -> tuple[Path, Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    stem = file_stem(run)
    md, html = outdir / f"{stem}.md", outdir / f"{stem}.html"
    n = 2
    while md.exists() or html.exists():
        md, html = outdir / f"{stem}-{n}.md", outdir / f"{stem}-{n}.html"
        n += 1
    md.write_text(render_markdown(run), encoding="utf-8")
    html.write_text(render_html(run), encoding="utf-8")
    return md, html
