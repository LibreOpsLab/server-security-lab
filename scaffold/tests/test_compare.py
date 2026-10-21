from pathlib import Path

import pytest

from sslab.compare import compare, render_comparison_html, render_comparison_markdown, write_comparison
from sslab.findings import Finding, Run


def F(id, sev="medium", layer="host"):
    return Finding(id, layer, f"title {id}", sev, "")


def R(label, findings, tool="lynis", host="docker01", not_run=None, metrics=None):
    return Run(label, tool, host, "alex", "alex/ssl", "10.10.0.0/24", "2026-11-16T01:00:00Z",
               findings, not_run or [], metrics or {})


def states(c):
    return {r.id: r.state for r in c.rows}


def test_each_state():
    before = R("default", [F("closed"), F("down", "high"), F("same"), F("gone-tool")])
    after = R("hardened", [F("down", "low"), F("same"), F("fresh")])
    assert states(compare(before, after)) == {
        "closed": "closed", "down": "reduced", "same": "unchanged", "gone-tool": "closed", "fresh": "new"}


def test_tool_not_run_after_is_not_compared_not_closed():
    c = compare(R("default", [F("a")]), R("hardened", [], not_run=["lynis"]))
    assert states(c) == {"a": "not_compared"}


def test_one_attack_not_run_only_affects_its_findings():
    before = R("default", [F("attack:web-basics:no-hsts"), F("attack:mail-basics:vrfy")], tool="attack-set")
    after = R("hardened", [], tool="attack-set", not_run=["web-basics"])
    assert states(compare(before, after)) == {
        "attack:web-basics:no-hsts": "not_compared", "attack:mail-basics:vrfy": "closed"}


def test_different_hosts_rejected():
    with pytest.raises(ValueError, match="different hosts"):
        compare(R("default", [F("a")]), R("hardened", [F("a")], host="samba-dc01"))


def test_empty_before_rejected_with_message():
    with pytest.raises(ValueError, match="before run has no findings"):
        compare(R("default", []), R("hardened", [F("a")]))


def test_empty_after_allowed_but_cautioned():
    md = render_comparison_markdown(compare(R("default", [F("a")]), R("hardened", [])))
    assert "1 closed" in md and "confirm the tool ran" in md


def test_summary_line_counts_each_state():
    before = R("default", [F("c1"), F("c2"), F("u"), F("n")])
    after = R("hardened", [F("u"), F("new1")], not_run=[])
    md = render_comparison_markdown(compare(before, after))
    assert md.splitlines()[2] == "3 closed, 0 reduced, 1 unchanged, 1 new, 0 not compared"


def test_gaps_are_listed_before_closed_findings():
    md = render_comparison_markdown(compare(R("default", [F("shut"), F("open")]), R("hardened", [F("open")])))
    assert md.index("title open") < md.index("title shut")


def test_metric_before_and_after_shown():
    c = compare(R("default", [F("a")], metrics={"hardening_index": "54"}), R("hardened", [F("a")], metrics={"hardening_index": "71"}))
    assert "hardening_index: 54 → 71" in render_comparison_markdown(c)


def test_html_and_write(tmp_path: Path):
    c = compare(R("default", [F("a")]), R("hardened", [F("a")]))
    assert "prefers-color-scheme: dark" in render_comparison_html(c)
    md, html = write_comparison(c, tmp_path)
    assert md.exists() and html.exists() and "compare" in md.name and "docker01" in md.name


def test_different_students_rejected_so_a_copied_after_run_is_not_credited():
    other = R("hardened", [F("a")])
    other.student = "sam"
    with pytest.raises(ValueError, match="different students"):
        compare(R("default", [F("a")]), other)


def test_different_forks_rejected():
    other = R("hardened", [F("a")])
    other.fork = "sam/ssl"
    with pytest.raises(ValueError, match="different students"):
        compare(R("default", [F("a")]), other)
