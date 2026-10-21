from pathlib import Path

from sslab.compare import compare
from sslab.findings import Finding, Run
from sslab.impact import impact_table


def R(label, findings):
    return Run(label, "attack-set", "docker01", "alex", "alex/ssl", "10.10.0.0/24", "2026-11-16T01:00:00Z", findings)


def F(id, title="Open port", sev="medium"):
    return Finding(id, "service", title, sev, "")


def test_impact_table_has_a_row_per_gap_and_closed_finding():
    before = R("default", [F("a", "Closed later"), F("b", "Still open"), F("c", "New-later")])
    after = R("hardened", [F("b", "Still open"), F("c", "New-later"), F("d", "Brand new")])
    md = impact_table(compare(before, after))
    for title in ("Closed later", "Still open", "Brand new"):
        assert title in md


def test_answer_columns_are_left_blank_for_the_student_to_fill():
    before = R("default", [F("a")])
    after = R("hardened", [])
    md = impact_table(compare(before, after))
    assert "| a |" in md.replace(" ", "") or "Open port" in md
    header = [ln for ln in md.splitlines() if ln.startswith("|")][0]
    assert "What could happen" in header and "business" in header.lower()
    rows = [ln for ln in md.splitlines() if ln.startswith("|") and "Open port" in ln][0]
    assert rows.rstrip("|").split("|")[-1].strip() == "" and rows.rstrip("|").split("|")[-2].strip() == ""


def test_hostile_finding_text_is_escaped():
    before = R("default", [F("a", title="<script>alert(1)</script> | x")])
    md = impact_table(compare(before, R("hardened", [])))
    assert "<script>" not in md
