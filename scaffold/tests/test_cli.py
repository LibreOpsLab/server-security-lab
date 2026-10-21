import shutil
import subprocess
from pathlib import Path

import pytest

from sslab.__main__ import main

FIX = Path(__file__).parent / "fixtures"
REPO = Path(__file__).parents[2]


def lynis(_cmd):
    return (FIX / "lynis-report.dat").read_text()


def lynis_hardened(_cmd):
    return "hardening_index=71\nsuggestion[]=AUTH-9286|Configure minimum password age|/etc/login.defs|-|\n"


@pytest.fixture
def env(tmp_path: Path):
    (tmp_path / "scope.txt").write_text("10.10.0.0/24\n")
    (tmp_path / "student.toml").write_text(
        'student = "alex"\nfork = "alex/server-security-lab"\n'
    )
    return tmp_path


def argv(env: Path, *a: str) -> list[str]:
    return [
        a[0],
        *a[1:],
        "--scope",
        str(env / "scope.txt"),
        "--student-config",
        str(env / "student.toml"),
        "--out",
        str(env / "reports"),
    ]


def test_audit_writes_json_markdown_and_html(env):
    assert (
        main(
            argv(
                env,
                "audit",
                "--label",
                "default",
                "--target",
                "10.10.0.5",
                "--tools",
                "lynis",
            ),
            runner=lynis,
        )
        == 0
    )
    names = sorted(p.suffix for p in (env / "reports").iterdir())
    assert names == [".html", ".json", ".md"]


def test_missing_scope_exits_nonzero_and_says_how_to_fix(env, capsys):
    (env / "scope.txt").unlink()
    assert (
        main(
            argv(
                env,
                "audit",
                "--label",
                "default",
                "--target",
                "10.10.0.5",
                "--tools",
                "lynis",
            ),
            runner=lynis,
        )
        == 2
    )
    assert "write your scope first" in capsys.readouterr().err


def test_out_of_scope_target_exits_nonzero(env, capsys):
    assert (
        main(
            argv(env, "attack", "--label", "default", "--target", "8.8.8.8"),
            runner=lynis,
        )
        == 2
    )
    assert "outside your lab range" in capsys.readouterr().err


def test_missing_student_config_exits_nonzero(env, capsys):
    (env / "student.toml").unlink()
    assert (
        main(
            argv(
                env,
                "audit",
                "--label",
                "default",
                "--target",
                "10.10.0.5",
                "--tools",
                "lynis",
            ),
            runner=lynis,
        )
        == 2
    )
    assert "student.toml" in capsys.readouterr().err


def test_tool_that_could_not_run_exits_1_but_still_writes_the_report(env):
    def broken(_cmd):
        raise FileNotFoundError("lynis")

    assert (
        main(
            argv(
                env,
                "audit",
                "--label",
                "hardened",
                "--target",
                "10.10.0.5",
                "--tools",
                "lynis",
            ),
            runner=broken,
        )
        == 1
    )
    assert any(p.suffix == ".md" for p in (env / "reports").iterdir())


def test_attack_writes_reports(env):
    assert (
        main(
            argv(env, "attack", "--label", "default", "--target", "10.10.0.5"),
            runner=lambda c: "<nmaprun/>" if "-oX" in c else "",
        )
        == 0
    )
    assert any(
        p.name.startswith("default-attack-set-") and p.suffix == ".md"
        for p in (env / "reports").iterdir()
    )


def test_compare_end_to_end(env):
    main(
        argv(
            env,
            "audit",
            "--label",
            "default",
            "--target",
            "10.10.0.5",
            "--tools",
            "lynis",
        ),
        runner=lynis,
    )
    main(
        argv(
            env,
            "audit",
            "--label",
            "hardened",
            "--target",
            "10.10.0.5",
            "--tools",
            "lynis",
        ),
        runner=lynis_hardened,
    )
    before = next((env / "reports").glob("default-lynis-*.json"))
    after = next((env / "reports").glob("hardened-lynis-*.json"))
    assert (
        main(
            [
                "compare",
                "--before",
                str(before),
                "--after",
                str(after),
                "--out",
                str(env / "reports"),
            ]
        )
        == 0
    )
    md = next((env / "reports").glob("compare-*.md")).read_text()
    assert "3 closed" in md and "hardening_index: 62 → 71" in md


def test_compare_empty_before_exits_nonzero(env, capsys):
    main(
        argv(
            env,
            "audit",
            "--label",
            "default",
            "--target",
            "10.10.0.5",
            "--tools",
            "lynis",
        ),
        runner=lambda c: "hardening_index=50\n",
    )
    main(
        argv(
            env,
            "audit",
            "--label",
            "hardened",
            "--target",
            "10.10.0.5",
            "--tools",
            "lynis",
        ),
        runner=lynis,
    )
    b = next((env / "reports").glob("default-lynis-*.json"))
    a = next((env / "reports").glob("hardened-lynis-*.json"))
    assert (
        main(
            [
                "compare",
                "--before",
                str(b),
                "--after",
                str(a),
                "--out",
                str(env / "reports"),
            ]
        )
        == 2
    )
    assert "no findings" in capsys.readouterr().err


@pytest.mark.skipif(
    shutil.which("shellcheck") is None, reason="shellcheck not installed"
)
def test_check_scripts_pass_shellcheck():
    scripts = [str(p) for p in REPO.glob("weeks/*/check.sh")]
    assert scripts, "no check.sh scripts found"
    assert subprocess.run(["shellcheck", *scripts]).returncode == 0


def test_impact_cli_writes_a_file(env):
    main(argv(env, "audit", "--label", "default", "--target", "10.10.0.5", "--tools", "lynis"), runner=lynis)
    main(argv(env, "audit", "--label", "hardened", "--target", "10.10.0.5", "--tools", "lynis"), runner=lynis_hardened)
    before = next((env / "reports").glob("default-lynis-*.json"))
    after = next((env / "reports").glob("hardened-lynis-*.json"))
    assert main(["impact", "--before", str(before), "--after", str(after), "--out", str(env / "reports")]) == 0
    assert next((env / "reports").glob("impact-*.md")).exists()


def test_impact_cli_rejects_different_students(env):
    main(argv(env, "audit", "--label", "default", "--target", "10.10.0.5", "--tools", "lynis"), runner=lynis)
    before = next((env / "reports").glob("default-lynis-*.json"))
    other = env / "reports" / "other.json"
    import json
    data = json.loads(before.read_text())
    data["student"] = "sam"
    other.write_text(json.dumps(data))
    assert main(["impact", "--before", str(before), "--after", str(other), "--out", str(env / "reports")], runner=lynis) == 2


def test_impact_cli_never_overwrites_an_existing_file(env):
    main(argv(env, "audit", "--label", "default", "--target", "10.10.0.5", "--tools", "lynis"), runner=lynis)
    main(argv(env, "audit", "--label", "hardened", "--target", "10.10.0.5", "--tools", "lynis"), runner=lynis_hardened)
    before = next((env / "reports").glob("default-lynis-*.json"))
    after = next((env / "reports").glob("hardened-lynis-*.json"))
    main(["impact", "--before", str(before), "--after", str(after), "--out", str(env / "reports")])
    first = next((env / "reports").glob("impact-*.md"))
    first.write_text(first.read_text() + "MY ANSWER HERE")
    main(["impact", "--before", str(before), "--after", str(after), "--out", str(env / "reports")])
    assert "MY ANSWER HERE" in first.read_text()  # the student's filled-in copy must not be clobbered
    assert len(list((env / "reports").glob("impact-*.md"))) == 2  # the new run gets its own file instead
