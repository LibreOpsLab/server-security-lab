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


def test_metrics_shown_in_both_formats():
    r = run(metrics={"hardening_index": "62"})
    assert "hardening_index" in render_markdown(r) and "62" in render_markdown(r)
    assert "hardening_index" in render_html(r)


HOSTILE = "x|y\n| forged | row |\n<script>alert(1)</script> [click](http://evil.example) `cmd` *b*"


def test_markdown_neutralises_hostile_finding_text():
    r = run(findings=[Finding("a", "host", HOSTILE, "high", HOSTILE)], student=HOSTILE, not_run=[HOSTILE], metrics={HOSTILE: HOSTILE})
    md = render_markdown(r)
    assert "<script>" not in md and "[click](" not in md and "forged" in md  # text kept, markup dead
    table_rows = [l for l in md.splitlines() if l.startswith("| ") and "high" in l]
    assert len(table_rows) == 1 and md.count("\n| forged") == 0  # no forged row starting a line
    assert all(l.startswith(("#", "-", "|", "<", "\\", " ")) or l == "" or "forged" not in l for l in md.splitlines())


def test_comparison_markdown_neutralises_hostile_text():
    from sslab.compare import compare, render_comparison_markdown

    a = run(findings=[Finding("a", "host", HOSTILE, "high", "")])
    md = render_comparison_markdown(compare(a, run(label="hardened", findings=[Finding("a", "host", HOSTILE, "high", "")])))
    assert "<script>" not in md and "[click](" not in md and "\n| forged" not in md
