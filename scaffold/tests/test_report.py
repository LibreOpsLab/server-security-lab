from pathlib import Path

from sslab.findings import Finding, Run
from sslab.report import render_html, render_markdown, write_reports


def run(**kw) -> Run:
    base = dict(
        label="default", tool="lynis", host="docker01", student="alex", fork="alex/server-security-lab",
        lab_range="10.10.0.0/24", started="2026-11-16T01:02:03Z",
        findings=[
            Finding("a", "host", "Low thing", "low", "minor"),
            Finding("b", "host", "Root login <allowed> & more", "high", "PermitRootLogin yes"),
            Finding("c", "network", "Open port", "medium", "22/tcp"),
        ],
        not_run=[],
    )
    base.update(kw)
    return Run(**base)


def test_markdown_header_carries_identifiers():
    md = render_markdown(run())
    for s in ("alex", "alex/server-security-lab", "docker01", "10.10.0.0/24", "default", "2026-11-16T01:02:03Z"):
        assert s in md


def test_markdown_groups_by_layer_and_sorts_high_first():
    md = render_markdown(run())
    assert md.index("## Network") < md.index("## Host")
    assert md.index("Root login") < md.index("Low thing")


def test_markdown_lists_not_run_tools():
    md = render_markdown(run(not_run=["nmap"]))
    assert "## Not run" in md and "nmap" in md


def test_empty_findings_is_not_called_clean():
    md = render_markdown(run(findings=[]))
    assert "No findings recorded. This is not the same as a clean result." in md


def test_html_escapes_finding_text():
    html = render_html(run())
    assert "&lt;allowed&gt; &amp; more" in html and "<allowed>" not in html


def test_html_has_dark_mode_and_brand_purple():
    html = render_html(run())
    assert "prefers-color-scheme: dark" in html and "#8547AD" in html


def test_write_reports_pairs_with_json_name(tmp_path: Path):
    md, html = write_reports(run(), tmp_path)
    assert md.suffix == ".md" and html.suffix == ".html" and md.stem == html.stem
    assert md.read_text().startswith("# ")
