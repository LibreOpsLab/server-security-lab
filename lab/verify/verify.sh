#!/usr/bin/env bash
# Smoke-test the whole lab. Each check prints PASS, FAIL or SKIP; any FAIL makes this exit 1.
# SKIP is for optional parts that are not built (Windows 11, a Wi-Fi access point); it is not a failure.
#
# Usage: verify.sh [--only NAME]
# Environment: VERIFY_TIMEOUT (seconds per check, default 30), VERIFY_CHECKS_DIR (for tests).
set -uo pipefail

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
dir=${VERIFY_CHECKS_DIR:-$here/checks}
limit=${VERIFY_TIMEOUT:-30}
only=""
if [ "${1:-}" = "--only" ]; then only=${2:?--only needs a check name}; fi

mapfile -t checks < <(find "$dir" -maxdepth 1 -name '[0-9]*-*.sh' | sort)
if [ -n "$only" ]; then
  selected=()
  for c in "${checks[@]}"; do
    n=$(basename "$c" .sh); n=${n#*-}
    [ "$n" = "$only" ] && selected+=("$c")
  done
  [ "${#selected[@]}" -gt 0 ] || { echo "no check named '$only'" >&2; exit 2; }
  checks=("${selected[@]}")
fi

passed=0 failed=0 skipped=0
for c in "${checks[@]}"; do
  n=$(basename "$c" .sh); n=${n#*-}
  out=$(timeout "$limit" bash "$c" 2>/dev/null)
  rc=$?
  if [ "$rc" -eq 124 ]; then out="FAIL $n timed out after ${limit}s"
  elif [ "$rc" -ne 0 ] || [ "$(printf '%s\n' "$out" | grep -c .)" -ne 1 ] || ! [[ $out =~ ^(PASS|FAIL|SKIP)\ [^\ ]+\  ]]; then
    out="FAIL $n check did not report one clear result (exit $rc)"
  fi
  echo "$out"
  case $out in PASS*) passed=$((passed + 1)) ;; SKIP*) skipped=$((skipped + 1)) ;; *) failed=$((failed + 1)) ;; esac
done

echo
echo "$passed passed, $failed failed, $skipped skipped"
[ "$failed" -eq 0 ]
