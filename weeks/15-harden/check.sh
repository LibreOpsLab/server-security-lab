#!/usr/bin/env bash
# Week 15: measure the hardened lab (label "hardened"). Usage: ./check.sh HOST [HOST...]
# Refuses to run for a host with no week 12 "default" audit, because there would be nothing to compare.
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH=scaffold
[ "$#" -gt 0 ] || { echo "usage: $0 HOST [HOST...]" >&2; exit 2; }
rc=0
for host in "$@"; do
  if [ -z "$(find portfolio/reports -name "default-*-$host-*.json" 2>/dev/null | head -1)" ]; then
    echo "no week 12 'default' report for $host: run weeks/12-baseline-attack/check.sh first" >&2
    rc=1
    continue
  fi
  python3 -m sslab audit --label hardened --target "$host" --tools "${TOOLS:-lynis,nmap}" || rc=1
done
exit "$rc"
