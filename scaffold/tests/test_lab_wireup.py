from pathlib import Path

REPO = Path(__file__).parents[2]


def test_readme_links_the_build_guides_and_states_unverified():
    readme = (REPO / "README.md").read_text()
    assert "docs/build/00-welcome.md" in readme
    assert "docs/design/lab-build-design.md" in readme
    assert "unverified" in readme.lower()


def test_ci_runs_the_lab_static_checks():
    ci = (REPO / ".github/workflows/ci.yml").read_text()
    assert "ansible" in ci.lower() and "yamllint" in ci and "make -C lab lint" in ci


def test_weak_defaults_doc_names_every_build_role_that_leaves_one():
    doc = (REPO / "docs/instructor-weak-defaults.md").read_text()
    for role in ("samba_dc", "mail", "files_server", "docker_host", "monitoring"):
        assert role in doc, role


def test_contributing_explains_how_to_verify_a_lab_component():
    contrib = (REPO / "CONTRIBUTING.md").read_text()
    assert "STATUS.md" in contrib and "unverified" in contrib.lower()


def test_changelog_mentions_the_lab_build():
    changelog = (REPO / "CHANGELOG.md").read_text()
    assert "lab build" in changelog.lower() or "business in a box" in changelog.lower()
