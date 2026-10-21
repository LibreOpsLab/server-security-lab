#!/usr/bin/env python3
"""Render the pfSense config.xml template from the lab inventory.

    render.py [--wan em0] [--lan em1] [--hostname pfsense01] [--vars FILE] [--out FILE]

The interface names are the ones pfSense showed at its "Assign Interfaces" console step (VMware's default
E1000 adapters are em0 and em1; the VMXNET3 adapters are vmx0 and vmx1). Needs Jinja2 and PyYAML, which
Ansible installs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import jinja2
import yaml

HERE = Path(__file__).parent
DEFAULT_VARS = HERE.parent / "inventory" / "group_vars" / "all.yml"


def render(variables: dict, wan: str, lan: str, hostname: str) -> str:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(HERE), undefined=jinja2.StrictUndefined, autoescape=True, keep_trailing_newline=True
    )
    return env.get_template("config.xml.j2").render(wan_if=wan, lan_if=lan, hostname=hostname, **variables)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wan", default="em0")
    ap.add_argument("--lan", default="em1")
    ap.add_argument("--hostname", default="pfsense01")
    ap.add_argument("--vars", type=Path, default=DEFAULT_VARS)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    try:
        variables = yaml.safe_load(args.vars.read_text(encoding="utf-8"))
        text = render(variables, args.wan, args.lan, args.hostname)
    except (OSError, yaml.YAMLError, jinja2.TemplateError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
