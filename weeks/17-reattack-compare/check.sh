#!/usr/bin/env bash
# Week 17: attack and audit the hardened lab with the same tools as week 12, then compare.
# Usage: ./check.sh HOST [HOST...]. Writes a comparison for each tool that has a default and a hardened run.
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH=scaffold
[ "$#" -gt 0 ] || { echo "usage: $0 HOST [HOST...]" >&2; exit 2; }
reports=portfolio/reports
latest() { find "$reports" -name "$1-$2-$3-*.json" | sort | tail -1; }
rc=0
for host in "$@"; do
  python3 -m sslab audit --label hardened --target "$host" --tools "${TOOLS:-lynis,nmap}" || rc=1
  python3 -m sslab attack --label hardened --target "$host" || rc=1
  for tool in $(echo "${TOOLS:-lynis,nmap}" | tr , " ") attack-set; do
    before=$(latest default "$tool" "$host"); after=$(latest hardened "$tool" "$host")
    if [ -z "$before" ] || [ -z "$after" ]; then echo "skipping $tool on $host: need a default and a hardened run" >&2; continue; fi
    python3 -m sslab compare --before "$before" --after "$after" --out "$reports" || rc=1
  done
done
exit "$rc"
