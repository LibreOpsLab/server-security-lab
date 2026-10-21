#!/usr/bin/env bash
# Week 12: measure the lab as built (label "default"). Usage: ./check.sh HOST [HOST...]
# Set TOOLS to change the audits, e.g. TOOLS=windows for a Windows host. Reports go to portfolio/reports/.
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH=scaffold
[ "$#" -gt 0 ] || { echo "usage: $0 HOST [HOST...]" >&2; exit 2; }
rc=0
for host in "$@"; do
  python3 -m sslab audit --label default --target "$host" --tools "${TOOLS:-lynis,nmap}" || rc=1
  python3 -m sslab attack --label default --target "$host" || rc=1
done
exit "$rc"
