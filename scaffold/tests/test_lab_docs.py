import re
from pathlib import Path

REPO = Path(__file__).parents[2]
BUILD = REPO / "docs" / "build"
GUIDES = [
    "00-welcome", "01-prepare-the-workstation", "02-pfsense", "03-proxmox", "04-admin01",
    "05-the-repo-inventory-and-secrets", "06-create-the-guests", "07-identity", "08-dns-dhcp-and-time",
    "09-squid", "10-docker-vm-and-apps", "11-single-sign-on", "12-mail", "13-file-transfer-and-shares",
    "14-wifi-radius", "15-monitoring-and-logs", "16-backup-and-restore", "17-windows-11-optional", "18-verify",
]
HEADINGS = ("What you will build", "Why", "Steps", "Check it worked", "If it goes wrong")
INSTITUTION_WORDS = ("tafe", "ictnwk", "ictnwk540", "ictnwk546", "college", "at1 ", "at2 ", "rto code")


def text(name):
    return (BUILD / f"{name}.md").read_text(encoding="utf-8")


def test_guides_exist_in_order_and_are_numbered_00_to_18():
    for i, name in enumerate(GUIDES):
        assert (BUILD / f"{name}.md").exists(), name
        assert name.startswith(f"{i:02d}-")


def test_every_guide_has_the_required_headings():
    for name in GUIDES:
        body = text(name)
        for h in HEADINGS:
            assert f"## {h}" in body, (name, h)


def test_welcome_opens_with_the_exact_line():
    assert text("00-welcome").lstrip().split("\n", 2)[0].strip() == "# Welcome"
    assert "Welcome, now let's build the LAB infrastructure we are going to need to complete this class." in text("00-welcome")


def test_relative_markdown_links_resolve():
    broken = []
    for name in GUIDES:
        body = text(name)
        for m in re.finditer(r"\]\(([^):#]+\.md[^)]*)\)", body):
            target = m.group(1).split("#")[0]
            if target.startswith(("http:", "https:")):
                continue
            if not (BUILD / target).resolve().exists() and not (REPO / target).resolve().exists():
                broken.append((name, target))
    assert not broken, broken


def test_no_institution_specific_wording_anywhere_in_the_public_repo():
    hits = []
    for base in (REPO / "docs", REPO / "lab"):
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in {".md", ".yml", ".yaml", ".j2", ".sh", ".conf"} and "secrets" not in p.parts:
                low = p.read_text(errors="ignore").lower()
                hits += [(p, w) for w in INSTITUTION_WORDS if w in low]
    assert not hits, hits


def test_status_lists_every_inventory_guest_as_unverified():
    import yaml
    status = (BUILD / "STATUS.md").read_text()
    guests = yaml.safe_load((REPO / "lab/inventory/group_vars/all.yml").read_text())["lab_hosts"]
    for name in guests:
        assert name in status, name
    assert status.lower().count("unverified") >= len(guests)


def test_week_map_references_every_guide():
    week_map = (BUILD / "WEEK-MAP.md").read_text()
    for name in GUIDES:
        assert name in week_map, name


def test_admin01_guide_generates_the_key_name_automation_expects():
    assert "lab_admin" in text("04-admin01")


def test_impact_commands_in_week_readmes_set_pythonpath():
    for wk in ("12-baseline-attack", "17-reattack-compare"):
        text = (REPO / "weeks" / wk / "README.md").read_text()
        assert "PYTHONPATH=scaffold python3 -m sslab impact" in text or "PYTHONPATH=scaffold python -m sslab impact" in text


def test_trust_or_identity_guide_notes_local_sudo_needs_handling():
    # 25-trust.yml and 30-identity.yml's localhost play both use become: true locally (admin01), which
    # needs either passwordless sudo or -K; a learner hitting "sudo: a password is required" needs a pointer.
    covered = any("-K" in text(g) or "passwordless sudo" in text(g).lower() for g in ("04-admin01", "05-the-repo-inventory-and-secrets", "07-identity"))
    assert covered
