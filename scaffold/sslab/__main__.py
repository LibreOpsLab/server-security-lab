"""Command line: audit, attack, compare. Run from the repo root as `PYTHONPATH=scaffold python -m sslab`."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Callable

from .attacks import run_attacks
from .collectors import COMMANDS, collect
from .compare import compare, write_comparison
from .impact import impact_table, impact_table_html
from .findings import Run, load_run, save_run
from .report import write_reports
from .scope import ScopeError, load_scope

Runner = Callable[[list[str]], str]


def audit_runner(cmd: list[str]) -> str:
    """Audits must succeed: a non-zero exit means the audit did not happen."""
    return subprocess.run(
        cmd, check=True, capture_output=True, text=True, timeout=900
    ).stdout


def attack_runner(cmd: list[str]) -> str:
    """Attacks report their result on stdout whatever the exit status; only a missing tool or a timeout raises."""
    return subprocess.run(
        cmd, check=False, capture_output=True, text=True, timeout=1800
    ).stdout


def _save(run: Run, out: Path) -> None:
    save_run(run, out)
    md, html = write_reports(run, out)
    print(f"wrote {md} and {html}")
    if run.not_run:
        print(
            f"NOT RUN: {', '.join(run.not_run)}. Fix and run again; this is not a clean result.",
            file=sys.stderr,
        )


def _student(path: Path) -> tuple[str, str]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return data["student"], data["fork"]
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        raise ScopeError(
            f'create {path} with student = "..." and fork = "..." (week 12 README)'
        ) from None


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--label", required=True, choices=["default", "hardened"])
    p.add_argument("--target", required=True)
    p.add_argument("--scope", type=Path, default=Path("portfolio/scope.txt"))
    p.add_argument(
        "--student-config", type=Path, default=Path("portfolio/student.toml")
    )
    p.add_argument("--out", type=Path, default=Path("portfolio/reports"))


def main(argv: list[str] | None = None, runner: Runner | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sslab", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("audit", help="audit a host with Lynis / nmap / a Windows audit")
    _common(a)
    a.add_argument(
        "--tools", default="lynis,nmap", help=f"comma list of: {', '.join(COMMANDS)}"
    )
    _common(sub.add_parser("attack", help="run the fixed attack set against a host"))
    c = sub.add_parser("compare", help="compare a default run with a hardened run")
    c.add_argument("--before", type=Path, required=True)
    c.add_argument("--after", type=Path, required=True)
    c.add_argument("--out", type=Path, default=Path("portfolio/reports"))
    i = sub.add_parser("impact", help="a blank table for the manager conversation: what each finding means for the business")
    i.add_argument("--before", type=Path, required=True)
    i.add_argument("--after", type=Path, required=True)
    i.add_argument("--out", type=Path, default=Path("portfolio/reports"))
    args = ap.parse_args(argv)
    try:
        if args.cmd in ("compare", "impact"):
            c = compare(load_run(args.before), load_run(args.after))
            if args.cmd == "compare":
                md, html = write_comparison(c, args.out)
            else:
                args.out.mkdir(parents=True, exist_ok=True)
                stem = f"impact-{c.before.host}-{args.after.stem}"
                md, html = args.out / f"{stem}.md", args.out / f"{stem}.html"
                # Never overwrite: the student fills this file in by hand, so a clash gets -2, -3, ...
                n = 2
                while md.exists() or html.exists():
                    md, html = args.out / f"{stem}-{n}.md", args.out / f"{stem}-{n}.html"
                    n += 1
                md.write_text(impact_table(c), encoding="utf-8")
                html.write_text(impact_table_html(c), encoding="utf-8")
            print(f"wrote {md} and {html}")
            return 0
        nets = load_scope(args.scope)
        student, fork = _student(args.student_config)
        failed = False
        if args.cmd == "audit":
            for tool in args.tools.split(","):
                run = collect(
                    tool.strip(),
                    args.target,
                    nets,
                    args.label,
                    student,
                    fork,
                    runner or audit_runner,
                )
                _save(run, args.out)
                failed |= bool(run.not_run)
        else:
            run = run_attacks(
                args.target, nets, args.label, student, fork, runner or attack_runner
            )
            _save(run, args.out)
            failed = bool(run.not_run)
        return 1 if failed else 0
    except (ScopeError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
