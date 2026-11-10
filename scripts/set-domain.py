#!/usr/bin/env python3
"""Change the lab's domain everywhere it is written down, from LAB_DOMAIN in the repo's .env file.

Usage:
  scripts/set-domain.py                  show what would change (a dry run)
  scripts/set-domain.py --apply          make the changes
  scripts/set-domain.py --docs --apply   also rewrite the guides (documentation) so they read the same

Where the new domain comes from, first match wins: --domain, the LAB_DOMAIN environment variable, LAB_DOMAIN in
.env at the repo root (see .env.example). The NetBIOS name (the short domain name, such as BOAB) is the first label
in capitals unless LAB_NETBIOS is set. The current domain is read from lab_domain in lab/inventory/group_vars/all.yml,
so running the script twice changes nothing the second time.

What it rewrites: the domain in lower case (boab.lab), as the Kerberos realm (BOAB.LAB), as directory names
(DC=boab,DC=lab) and the NetBIOS name, in lab/ (inventory, Docker stacks, PKI config, scripts, Windows join script).
It never touches CHANGELOG.md, the tests, .git, node_modules or lab/secrets.

Do this BEFORE you build anything. A domain controller cannot be renamed: if samba-dc01 already exists, rebuild it.

Note for learners with a private copy: this edits tracked files, so `git merge upstream/main` may later report
conflicts in them. Commit the change on its own first, and resolve conflicts by keeping your domain.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = "lab/inventory/group_vars/all.yml"
SKIP_DIRS = {".git", "node_modules", "__pycache__", "secrets", "_site", ".pytest_cache"}
SKIP_FILES = {"CHANGELOG.md"}
SKIP_PREFIXES = ("scaffold/tests/",)
DOC_DIRS = ("docs/", "weeks/")
DOC_FILES = ("README.md",)
GENERATED = {"docs/company/org-chart.md"}  # rebuilt by scripts/gen-org-chart.py instead of rewritten
LABEL = r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
DOMAIN_RE = re.compile(rf"^{LABEL}(?:\.{LABEL})+$")


def read_env(path: Path) -> dict:
    out = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip().strip("'\"")
    return out


def current_domain(root: Path) -> str:
    m = re.search(r"^lab_domain:\s*(\S+)", (root / INVENTORY).read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"Could not find lab_domain in {INVENTORY}.")
    return m.group(1)


def current_netbios(root: Path) -> str:
    m = re.search(r"^lab_netbios:\s*(\S+)", (root / INVENTORY).read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else ""


def netbios_for(domain: str, given: str | None) -> str:
    name = (given or domain.split(".")[0]).upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9-]{0,14}", name):
        sys.exit(f"'{name}' is not a valid NetBIOS name: use 1 to 15 letters, digits or hyphens (set LAB_NETBIOS).")
    return name


def dn(domain: str, case: str) -> str:
    return ",".join(f"{case}{p}" for p in domain.split("."))


def replacements(old: str, new: str, old_nb: str, new_nb: str) -> list[tuple[str, str]]:
    """Literal (old, new) pairs for the domain in its four spellings, then the NetBIOS name."""
    return [
        (dn(old, "DC="), dn(new, "DC=")),
        (dn(old, "dc="), dn(new, "dc=")),
        (old.upper(), new.upper()),
        (old, new),
    ]


def rewrite(text: str, pairs, old_nb: str = "", new_nb: str = "") -> str:
    # One pass over the original text, so a new domain that contains the old one is not rewritten twice.
    table = dict(pairs)
    pattern = re.compile("|".join(re.escape(k) for k in sorted(table, key=len, reverse=True)))
    text = pattern.sub(lambda m: table[m.group(0)], text)
    if old_nb and old_nb != new_nb:
        text = re.sub(rf"(?m)^(lab_netbios:\s*){re.escape(old_nb)}\s*$", rf"\g<1>{new_nb}", text)
        text = re.sub(rf"\b{re.escape(old_nb)}(?=\\)", new_nb, text)  # the NetBIOS name before a backslash, as in the sign-in name NAME\user
    return text


def targets(root: Path, docs: bool):
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        rel = path.relative_to(root).as_posix()
        if rel in SKIP_FILES or rel in GENERATED or rel.startswith(SKIP_PREFIXES):
            continue
        in_lab = rel.startswith("lab/")
        in_docs = rel.startswith(DOC_DIRS) or rel in DOC_FILES
        if not (in_lab or (docs and in_docs)):
            continue
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary
        yield path, rel


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--domain", help="the new domain (default: LAB_DOMAIN from the environment or .env)")
    ap.add_argument("--netbios", help="the new NetBIOS name (default: first label in capitals, or LAB_NETBIOS)")
    ap.add_argument("--env", help="path of the .env file (default: .env at the repo root)")
    ap.add_argument("--docs", action="store_true", help="also rewrite the guides in docs/ and weeks/")
    ap.add_argument("--apply", action="store_true", help="make the changes (default is a dry run)")
    ap.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    root = Path(args.root)

    env = read_env(Path(args.env) if args.env else root / ".env")
    new = (args.domain or os.environ.get("LAB_DOMAIN") or env.get("LAB_DOMAIN") or "").strip().lower()
    if not new:
        sys.exit("No domain given. Set LAB_DOMAIN in .env (copy .env.example), or pass --domain.")
    if not DOMAIN_RE.match(new):
        sys.exit(f"'{new}' is not a valid domain name: use lower-case labels separated by dots, such as boab.lab.")
    if new.endswith(".local"):
        print("Warning: .local is used by multicast DNS and causes odd name-lookup problems. Prefer something else.")
    old = current_domain(root)
    new_nb = netbios_for(new, args.netbios or os.environ.get("LAB_NETBIOS") or env.get("LAB_NETBIOS"))
    old_nb = current_netbios(root)
    if new == old and new_nb == old_nb:
        print(f"The lab domain is already {old} (NetBIOS {old_nb}). Nothing to change.")
        return 0

    pairs = replacements(old, new, old_nb, new_nb)
    changed = []
    for path, rel in targets(root, args.docs):
        text = path.read_text(encoding="utf-8")
        out = rewrite(text, pairs, old_nb, new_nb)
        if out != text:
            changed.append((path, rel, out))
    print(f"Domain {old} -> {new}   NetBIOS {old_nb} -> {new_nb}")
    for _, rel, _ in changed:
        print(f"  {'changed' if args.apply else 'would change'}  {rel}")
    print(f"{len(changed)} file(s) {'changed' if args.apply else 'would change'}.")
    if not args.apply:
        print("Dry run. Add --apply to make the changes.")
        return 0
    for path, _, out in changed:
        path.write_text(out, encoding="utf-8", newline="")
    gen = root / "scripts" / "gen-org-chart.py"
    if args.docs and gen.is_file() and (root / "docs/company/org-chart.md").is_file():
        subprocess.run([sys.executable, str(gen)], check=False)
    print("Done. Check `git diff`, then continue with the build guides.")
    if not args.docs:
        print("The guides still show the old domain. Add --docs to update them too.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
